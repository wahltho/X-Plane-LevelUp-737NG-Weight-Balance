# LevelUp 700/800 ACF reconcile

Date: 2026-08-20

Status: source reconcile and static verification only; no deploy or simulator
runtime test.

## Inputs

| Role | 737-700 | 737-800 |
|---|---|---|
| Jochen input | `/Users/wahltho/Downloads/Level Up/737_70NG.acf` | `/Users/wahltho/Downloads/Level Up/737_80NG-2.acf` |
| Input SHA-256 | `8cb0d7254e63cd1a2b4fe88071e706393504e6bfce7ab6af3cca417d22ea3c31` | `9315f4110ae8c2b5feb53872ae3d7a6bcc2ff380099b6c925c9734d2d65fbe16` |
| Previous overlay | `overlay/LU 737NG Series/737_70NG.acf` | `overlay/LU 737NG Series/737_80NG.acf` |
| Previous overlay SHA-256 | `71a468075ad6c8e063ede3f893c644e770454a65fc397bc34959fa16dc61c679` | `e7a6b03f533614711a8af86575aa702d22c9077d1a6110eb30f838aa06c533b7` |
| Reconciled overlay SHA-256 | `a5d2cdd9e7dec57ec42d22a0937f3c08ee56e1adbd7334b87bbfd38fb9a811f2` | `e3bb89129fc2400581fec27e8b2c2947a99b06e0aefc24cb3d40a833fc0f5c1c` |

The current LevelUp Git baseline at
`/Users/wahltho/dev/LevelUp/737NG-Series` was the common ancestor for the
semantic three-way classification.

## Findings

The Jochen files cannot replace the overlay files as whole files. Their
flightmodel and W&B records are newer, but their object tables use the public
LevelUp layout. A whole-file replacement would reintroduce `jdcopilot.obj`,
remove the private Collins WXR objects and alter the private cockpit/default
view.

The three-way P-record comparison produced:

| Variant | Jochen-only | Overlay-only | true conflicts |
|---|---:|---:|---:|
| 737-700 | 9,995 | 25 | 4 |
| 737-800 | 6,751 | 4 | 15 |

Most Jochen-only records are wing/flightmodel records. The true non-object
conflicts are V2.S1.51 metadata, equilibrium values and, for the -800, flap
coefficients. Jochen is the intended owner of those flightmodel values, so the
latest Jochen values win. The private overlay remains owner of object slots,
Collins WXR integration, removal of the JAR copilot stub and transformed
cockpit/quickview properties.

## Merge contract

- Take Jochen's V2.S1.51 flightmodel, wing, control, mass, CG, station and tank
  P-records.
- Preserve the complete overlay `_obja/*` domain.
- Preserve `acf/_pe_xyz/*` and `acf/_ang_offset/0,1`, which are private
  cockpit/default-view properties rather than flightmodel tuning.
- Preserve unrelated overlay-only custom fields when Jochen retained the
  common LevelUp baseline value.
- Take Jochen's W&B fields even when a previous overlay value also differed
  from the baseline.
- Keep LF line endings.

## W&B result

The reconciled overlay now satisfies the same semantic contracts consumed by
the public W&B package:

- 737-700: `levelup700-wb-v1`;
- 737-800: `levelup800-wb-v2`.

The latest -700 file changes no consumed W&B value relative to the existing
`levelup700-wb-v1` contract. It only changes whole-file provenance and
unrelated V2.S1.51 flightmodel fields. The latest -800 input is already the
source of the v2 contract introduced by package v0.2.1. Package v0.2.2
therefore synchronizes exact provenance and upgrade testing; it deliberately
does not change the v0.2.1 W&B equations.

## Static acceptance

The merged files must retain these invariants:

| Invariant | 737-700 | 737-800 |
|---|---:|---:|
| Object count | 42 | 41 |
| `jdcopilot.obj` | absent | absent |
| Collins WXR knobs/panel | present | present |
| Jochen version | `XP12 2.S1.51 (20260819 2130 SAO)` | `XP12 FM V2.S1.51 (20260819 1920 SAO)` |
| Active stations | 9 | 9 |

Flightmodel behavior, cockpit view, object loading and W&B behavior remain
runtime-open until a separately approved simulator test.
