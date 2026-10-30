# Minimal original shop example

A tiny procedural shop shell with counter/register, display shelves, table and two chairs. All geometry is created from neutral primitives in an empty scene; no old project, downloaded asset, texture or plug-in is loaded. This is a runnable example, not a new independent cold-context evaluation.

## Run from repository root

Requires Linux, Python 3 and Blender 4.3-compatible CLI. First check available memory; the default 2 GiB sampled RSS cap is configurable, not a universal machine budget.

```sh
python3 examples/minimal-shop/run_example.py --output ./runs/shop-001
```

Optional: `--blender /path/to/blender --timeout 120 --max-rss-mib 2048`. Only one Blender process runs at a time, with 2 threads. Each process has a bounded timeout/RSS guard. The output directory must not already exist; a partial failed run is kept for diagnosis, and retry uses a new directory. Existing files are never silently replaced.

## Outputs

- `shop.blend` and `shop.glb`: complete, static, metric native/export scene, 6×4 m shell, Z up and front −Y. No glass, animation or authored beauty materials.
- `white-overview.png`: intact exterior; `white-roof-off-top.png`: temporary roof removal; `white-furniture-closeup.png`: rear/left/roof cutaway retaining the relevant right wall and front framing for furniture clearance.
- `overlap-review.json`: conservative world-AABB candidate/contact/exemption categories; **not actual-mesh penetration certification**.
- `allowlist.json`: exact named structural-joint pairs with reasons. No broad category-based bypasses.
- `native.json`, `glb.json`, `verification.json`: fresh native/GLB inventory, names/world bounds/triangle parity, preserved roof, source immutability, artifact hashes and elapsed time.
- `*-resources.json` and logs: per-process sampled RSS and elapsed time. These runtime logs contain machine-local paths; review/redact before sharing them.

The builder saves and exports before preview-only camera/visibility changes. The runner reopens the saved native file and imports the GLB in another fresh process. Still view the actual PNGs: geometry counts or a zero-candidate broad-phase result do not establish visual quality, usable access, or building-code compliance. Run the included regression suite from the repository root with `python3 -m unittest discover -s tests -p 'test_*.py' -v`.
