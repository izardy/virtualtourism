"""Whole web-model build from the digital twin, in background Blender (never touches a file open in the Blender UI):

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python blender/scripts/twin_pipeline.py
    sh blender/scripts/optimize_glb.sh && sh blender/scripts/optimize_glb.sh mobile

Steps: twin_build.py (scene from blender/penang_war_museum) -> place_props.py (Poly Haven trees, understory, rocks)
-> export_muzium.py (desktop GLB) -> build_tour_paths.py (guided-tour routes) -> export_mobile.py (phone GLB).
"""
import time
R = "/Users/izardy/Documents/virtualtourism/blender/scripts/"
for f in ("twin_build.py", "place_props.py", "export_muzium.py", "build_tour_paths.py", "export_mobile.py"):
    t = time.time()
    print("=" * 20, f, flush=True)
    exec(open(R + f).read(), {"__name__": "__main__", "__file__": R + f})
    print("=" * 20, f, "done in", round(time.time() - t), "s", flush=True)
