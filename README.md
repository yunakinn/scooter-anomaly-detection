# Scooter Parking Detection

A prototype that connects scooter parking detection to report management and pickup route planning.

**Object detection · Streamlit · Geospatial visualization**

[Dashboard](dashboard/app.py) · [Detector](src/detector.py) · [Route planner](src/route_optimizer.py)

## Overview

The application accepts a reported image and location, detects normal or abnormal parking, and turns the result into a scored event. An administrator view supports filtering reports, tracking their status, and planning a pickup route across predefined campus locations.

The repository includes the dashboard, inference and scoring logic, route planning, experiment notebooks, and sample images. Trained detector weights are not included.

## Example Inputs

These are repository sample inputs, not model predictions or evidence of detection accuracy.

<table>
<tr>
<td align="center"><img src="data/demo_images/normal.jpg" width="340" alt="Sample input stored as normal.jpg"><br>Normal parking sample</td>
<td align="center"><img src="data/demo_images/abnormal.jpg" width="340" alt="Sample input stored as abnormal.jpg"><br>Abnormal parking sample</td>
</tr>
</table>

## Workflow

```mermaid
flowchart LR
    I["Image + report location"] --> Y["YOLO detector"]
    Y --> D["Boxes + class confidence"]
    D --> S["Violation score"]
    S --> E["Report event"]
    E --> A["Admin filters and status tracking"]
    A --> R["Pickup targets"]
    R --> M["Route order + map"]
```

### Detection and scoring

[Detector](src/detector.py) loads a YOLO checkpoint and collects bounding boxes, labels, and confidence values. It chooses an abnormal prediction first when the maximum abnormal confidence reaches 0.5; otherwise it checks normal confidence, then returns `none` if neither reaches the threshold.

[RiskScorer](src/risk_scorer.py) converts the maximum abnormal confidence into a score:

```text
score = round(maximum abnormal confidence × 100, 1)
```

| Score | Display level | Suggested action |
| :--- | :--- | :--- |
| 80–100 | Very high | Immediate review and pickup |
| 50–<80 | High | On-site review |
| 30–<50 | Low | Monitor |
| 0–<30 | Normal | Likely normal parking |

This is a confidence-based prioritization heuristic, not a calibrated measure of physical danger or a legal determination of a parking violation.

### Pickup route planning

The route planner selects reports with an `abnormal` prediction, score of at least 50, and a known location.

- Default start: the campus main building.
- Up to eight targets: exhaustive search for the shortest visit order under the implemented distance approximation.
- More than eight targets: a nearest-neighbor heuristic.
- Distances: planar estimates between fixed coordinates, without road or pedestrian-network routing.
- The route is an open path; it does not include a return trip to the start.

## Getting Started

Run commands from the repository root. Use Python 3.10 or later.

```bash
git clone https://github.com/yunakinn/scooter-anomaly-detection.git
cd scooter-anomaly-detection
python -m venv .venv
source .venv/bin/activate
python -m pip install streamlit ultralytics folium streamlit-folium plotly pandas
```

There is currently no dependency manifest or pinned environment in this repository. The command above lists the application's directly imported third-party packages; it is not a tested lockfile.

### Start the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard starts with eight hard-coded demonstration events. These illustrate the administrator workflow; their scores are not evaluation results. Submitting a new image for analysis additionally requires detector weights.

### Enable image inference

Place a compatible trained YOLO checkpoint at:

```text
weights/best.pt
```

Or provide its path when launching:

```bash
MODEL_PATH=/absolute/path/to/best.pt streamlit run dashboard/app.py
```

The detector expects class names `normal` and `abnormal`. If checkpoint class names are unavailable, the fallback mapping is 0 → normal and 1 → abnormal.

The map optionally reads `VWORLD_API_KEY`; otherwise it uses the fallback tiles configured in [map_tiles.py](dashboard/map_tiles.py).

## Repository Guide

| Path | Purpose |
| :--- | :--- |
| [dashboard/](dashboard/) | Report submission, administrator view, styling, and maps |
| [src/detector.py](src/detector.py) | YOLO inference and annotated results |
| [src/risk_scorer.py](src/risk_scorer.py) | Confidence-to-score mapping and action levels |
| [src/event_system.py](src/event_system.py) | Event creation and report locations |
| [src/route_optimizer.py](src/route_optimizer.py) | Target selection and visit ordering |
| [src/visualization.py](src/visualization.py) | Event statistics and charts |
| [notebooks/](notebooks/) | Data processing and YOLO / RT-DETR experiment notebooks |
| [data/demo_images/](data/demo_images/) | Sample input images |
| [dataset.yaml](dataset.yaml) | Training dataset configuration requiring local paths |

## Current Scope and Limitations

- No consolidated held-out evaluation metrics are published in this README; sample inputs and demo events should not be read as measured performance.
- Report state is held in Streamlit session state rather than a persistent database. Uploaded images are saved locally under `data/uploaded_images/`.
- Locations and route assumptions are specific to the predefined campus map.
- Reproducing model training requires the dataset and an appropriate training setup beyond the included sample images.

