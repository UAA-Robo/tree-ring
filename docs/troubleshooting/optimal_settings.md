# Optimal Settings for the Camera

The camera has a number of defaults for its image settings. However, through testing these have been found to be sub-optimal. The following table demonstrates the default and optimal settings for each camera setting.


| Camera Setting         | Range     | Default  | Optimal   |
| ---------------------- | --------- | -------- | --------- |
| Auto-Expo Enabled      | 1/0       |  1       |  0        |
| Auto Exposure Target   |   16~235  |  120     |  120      |
| Temperature            | 2000~15000|  6503    |  11616    |
| Tint                   | 200~2500  |  1000    |  925      |
| Level Range            | 0~255 x 4 | L(0,0,0,0) H(255,255,255,255)    | L(0,0,0,0) H(255,255,255,255)   |
| Contrast               | -100~100  |  0       |  0        |
| Hue                    | -180~180  |  0       |  0        |
| Saturation             | 0~255     |  128     |  126      |
| Brightness             | -64~64    |  0       |  -64      |
| Gamma                  | 20~180    |  100     |  100      |
| WBGain                 | -127~127 x 3   |  (0,0,0)       |  (0,0,0)       |
| Sharpening             | 0~500     |  0       |  500      |
| Linear Tone Mapping    | 1/0       |  1       |  0        |
| Curved Tone Mapping    | 2/1/0     |  2 (Logarithmic)     |  1 (Polynomial)      |


To configure the camera to the optimal settings, copy the following text block into a file called
`camera_configuration.yaml` in the directory where the program's exe is in.

**For a Leica KL 1500LCD light:**
```yaml
auto_expo: 0
brightness: 16
contrast: 0
curve: Polynomial
exposure: 50
fformat: tiff
gamma: 100
hue: 0
levelrange_high:
- 255
- 255
- 255
- 255
levelrange_low:
- 0
- 0
- 0
- 0
linear: 0
saturation: 96
sharpening: 500
temp: 6503
tint: 1000
wbgain:
- 0
- 0
- 0

```

**For a ring light:**
```yaml
auto_expo: 0
brightness: -64
contrast: 0
curve: Polynomial
exposure: 120
fformat: tiff
gamma: 100
hue: 0
levelrange_high:
- 255
- 255
- 255
- 255
levelrange_low:
- 0
- 0
- 0
- 0
linear: 0
saturation: 126
sharpening: 500
temp: 11616
tint: 925
wbgain:
- 0
- 0
- 0

```