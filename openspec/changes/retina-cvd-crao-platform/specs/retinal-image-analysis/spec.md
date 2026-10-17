# Spec Delta

## Purpose

Turns a quality-accepted fundus photograph into model outputs a clinician can check: anatomical segmentation, an attention heatmap, a calibrated probability with a confidence band, and a plain-language explanation of what the model looked at and why it may be wrong.

## ADDED Requirements

### Requirement: Anatomical segmentation overlay
For every analysed image the system SHALL produce overlays for retinal vessels, arteries vs veins, and the optic disc, and SHALL estimate the fovea location. The overlays SHALL be viewable on top of the original image with adjustable opacity and toggles for each layer.

#### Scenario: Overlays shown with controls
- **WHEN** analysis finishes on an accepted image
- **THEN** the result view shows the original image with toggleable vessel, artery/vein and optic-disc layers and an opacity slider

#### Scenario: Segmentation failure is visible
- **WHEN** the optic disc cannot be located
- **THEN** the system says so, omits region-based explanation, and does not invent a disc position

### Requirement: Attention heatmap in Emergency mode
In Emergency mode the system SHALL produce a heatmap of the image regions that most influenced the CRAO probability, viewable as an overlay and side by side with the original.

#### Scenario: Heatmap displayed
- **WHEN** Emergency-mode analysis finishes
- **THEN** the clinician can view the heatmap overlay, change its opacity, and compare it side by side with the unaltered image

#### Scenario: Heatmap labelled as non-diagnostic
- **WHEN** a heatmap is shown
- **THEN** the view states that the heatmap shows model attention, not confirmed lesions

### Requirement: Calibrated probability with confidence band
The system SHALL report the CRAO probability as a calibrated value (0 to 1) and SHALL map it to a band: "unlikely", "uncertain" or "likely", using configurable thresholds. The model version and calibration date SHALL be shown with every probability.

#### Scenario: Probability in the uncertain band
- **WHEN** the calibrated probability falls between the low and high thresholds
- **THEN** the system labels the result "uncertain", recommends specialist review, and does not present it as a positive or negative finding

#### Scenario: Version shown
- **WHEN** any probability is displayed
- **THEN** the model identifier, version and calibration date are displayed next to it

### Requirement: Region-based explanation
The system SHALL generate a short explanation from structured outputs only: probability, band, quality score, the anatomical region holding most heatmap mass (macula, optic disc, vascular arcades or periphery), and fixed limitation statements. Explanations SHALL be built from fixed templates, with no free-text generation.

#### Scenario: Explanation names the region
- **WHEN** most of the heatmap mass lies within the macular region
- **THEN** the explanation states that the model focused on the macula, notes that CRAO typically whitens the macula and can produce a cherry-red spot, and asks the clinician to confirm on the image

#### Scenario: Explanation states limitations
- **WHEN** any Emergency-mode explanation is produced
- **THEN** it includes that the model was trained on established (not hyperacute) artery occlusions and that an early CRAO can look normal on a fundus photo

### Requirement: Retinal vascular measurements
In Screening mode the system SHALL compute retinal vascular measurements from the segmentation: artery calibre, vein calibre and artery-to-vein ratio. Each SHALL be reported with its value and a reference interval label.

#### Scenario: Measurements reported
- **WHEN** Screening-mode analysis finishes on an accepted image
- **THEN** the result shows arteriolar calibre, venular calibre and artery-to-vein ratio, each flagged "within reference" or "outside reference"

### Requirement: Degraded operation without model weights
If the disease model weights are not loaded, the system SHALL still run the quality gate and segmentation, SHALL report "no model loaded" instead of a probability, and SHALL route Emergency-mode cases to escalation.

#### Scenario: No weights present
- **WHEN** the CRAO model weights are missing at start-up
- **THEN** Emergency-mode results show "no model loaded" and the triage level is ESCALATE
