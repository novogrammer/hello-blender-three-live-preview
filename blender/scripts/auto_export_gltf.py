import bpy
from bpy.app.handlers import persistent
from pathlib import Path

COLLECTION_NAME = "Export"

def find_layer_collection(layer_collection, name):
    if layer_collection.collection.name == name:
        return layer_collection
    for child in layer_collection.children:
        found = find_layer_collection(child, name)
        if found:
            return found
    return None

@persistent
def auto_export(_):
    if not bpy.data.filepath:
        return

    # コレクション切り替え
    root = bpy.context.view_layer.layer_collection
    target = find_layer_collection(root, COLLECTION_NAME)
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

# 登録
handlers = bpy.app.handlers.save_post
for h in list(handlers):
    if getattr(h, "__name__", "") == "auto_export":
        handlers.remove(h)

handlers.append(auto_export)