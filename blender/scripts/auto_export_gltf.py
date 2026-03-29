import bpy
from pathlib import Path

EXPORT_TARGET_COLLECTION_NAME = "ExportTarget"
MODE_SET_BY_CONTEXT_MODE = {
    "EDIT_CURVE": "EDIT",
    "EDIT_MESH": "EDIT",
    "EDIT_SURFACE": "EDIT",
    "EDIT_TEXT": "EDIT",
    "EDIT_ARMATURE": "EDIT",
    "EDIT_METABALL": "EDIT",
    "EDIT_LATTICE": "EDIT",
    "POSE": "POSE",
    "SCULPT": "SCULPT",
    "PAINT_WEIGHT": "WEIGHT_PAINT",
    "PAINT_VERTEX": "VERTEX_PAINT",
    "PAINT_TEXTURE": "TEXTURE_PAINT",
    "PARTICLE": "PARTICLE_EDIT",
    "OBJECT": "OBJECT",
}


def find_collection_in_tree(root_collection, name):
    if root_collection.name == name:
        return root_collection
    for child in root_collection.children:
        found = find_collection_in_tree(child, name)
        if found:
            return found
    return None


def get_export_collection(source_scene):
    source_collection = find_collection_in_tree(
        source_scene.collection,
        EXPORT_TARGET_COLLECTION_NAME,
    )
    if source_collection is None:
        raise RuntimeError(
            f'Collection "{EXPORT_TARGET_COLLECTION_NAME}" was not found in scene "{source_scene.name}"'
        )
    return source_collection


def rebuild_and_export(context):
    export_collection = get_export_collection(context.scene)
    previous_mode = bpy.context.mode
    previous_mode_set = MODE_SET_BY_CONTEXT_MODE.get(previous_mode, "OBJECT")

    try:
        if previous_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        blend_dir = Path(bpy.data.filepath).parent
        export_path = blend_dir.parent / "public/models/scene.glb"

        bpy.ops.export_scene.gltf(
            filepath=str(export_path),
            export_format='GLB',
            collection=export_collection.name,
            export_apply=True,
        )
    finally:
        if previous_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=previous_mode_set)

    return export_collection


class EXPORT_OT_auto_gltf(bpy.types.Operator):
    bl_idname = "export_scene.auto_gltf"
    bl_label = "Export Auto GLB"
    bl_description = "Export the ExportTarget collection to scene.glb"

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save the .blend file before exporting")
            return {'CANCELLED'}

        try:
            rebuild_and_export(context)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}

        self.report({'INFO'}, "Exported scene.glb")
        return {'FINISHED'}


class VIEW3D_PT_auto_gltf_export(bpy.types.Panel):
    bl_label = "Auto GLB Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        layout.operator(EXPORT_OT_auto_gltf.bl_idname, icon='EXPORT')


CLASSES = (
    EXPORT_OT_auto_gltf,
    VIEW3D_PT_auto_gltf_export,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
