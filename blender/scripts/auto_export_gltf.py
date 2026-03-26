import bpy
from bpy.app.handlers import persistent
from pathlib import Path

MODELING_COLLECTION_NAME = "Modeling"
EXPORT_COLLECTION_NAME = "Export"
APPLY_MODIFIER_TYPES = {
    "BEVEL",
    "DATA_TRANSFER",
    "EDGE_SPLIT",
    "NODES",
    "NORMAL_EDIT",
    "SOLIDIFY",
    "SUBSURF",
    "TRIANGULATE",
    "WEIGHTED_NORMAL",
    "WELD",
}
COPY_DATA_OBJECT_TYPES = {
    "CURVE",
    "FONT",
    "MESH",
    "META",
    "SURFACE",
}


def find_layer_collection(layer_collection, name):
    if layer_collection.collection.name == name:
        return layer_collection
    for child in layer_collection.children:
        found = find_layer_collection(child, name)
        if found:
            return found
    return None


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection:
        return collection

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def clear_collection(collection):
    for obj in list(collection.objects):
        collection.objects.unlink(obj)
        if obj.users == 0:
            bpy.data.objects.remove(obj)


def duplicate_collection_objects(source_collection, target_collection):
    object_map = {}

    for obj in source_collection.all_objects:
        duplicate = obj.copy()
        if obj.data and obj.type in COPY_DATA_OBJECT_TYPES:
            duplicate.data = obj.data.copy()
        target_collection.objects.link(duplicate)
        object_map[obj] = duplicate

    for source, duplicate in object_map.items():
        if source.parent in object_map:
            duplicate.parent = object_map[source.parent]
            duplicate.matrix_parent_inverse = source.matrix_parent_inverse.copy()

    for duplicate in object_map.values():
        for modifier in duplicate.modifiers:
            if hasattr(modifier, "object") and modifier.object in object_map:
                modifier.object = object_map[modifier.object]

    return list(object_map.values())


def apply_selected_modifiers(objects):
    view_layer = bpy.context.view_layer
    previous_active = view_layer.objects.active
    previously_selected = list(bpy.context.selected_objects)

    bpy.ops.object.select_all(action='DESELECT')

    try:
        for obj in objects:
            if obj.type != "MESH":
                continue

            for modifier in list(obj.modifiers):
                if modifier.type not in APPLY_MODIFIER_TYPES:
                    continue

                view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                obj.select_set(False)
    finally:
        view_layer.objects.active = previous_active
        for obj in previously_selected:
            if obj.name in bpy.data.objects:
                obj.select_set(True)


def rebuild_export_collection():
    source_collection = bpy.data.collections.get(MODELING_COLLECTION_NAME)
    if source_collection is None:
        raise RuntimeError(f'Collection "{MODELING_COLLECTION_NAME}" was not found')

    export_collection = ensure_collection(EXPORT_COLLECTION_NAME)
    clear_collection(export_collection)
    export_objects = duplicate_collection_objects(source_collection, export_collection)
    apply_selected_modifiers(export_objects)
    return export_collection


@persistent
def auto_export(_):
    if not bpy.data.filepath:
        return

    export_collection = rebuild_export_collection()

    root = bpy.context.view_layer.layer_collection
    target = find_layer_collection(root, export_collection.name)
    if target:
        bpy.context.view_layer.active_layer_collection = target

    blend_dir = Path(bpy.data.filepath).parent
    export_path = blend_dir.parent / "public/models/scene.glb"

    bpy.ops.export_scene.gltf(
        filepath=str(export_path),
        export_format='GLB',
        use_active_collection=True,
    )

    print("exported collection")


handlers = bpy.app.handlers.save_post
for h in list(handlers):
    if getattr(h, "__name__", "") == "auto_export":
        handlers.remove(h)

handlers.append(auto_export)
