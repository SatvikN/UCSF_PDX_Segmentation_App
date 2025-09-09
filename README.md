# PDX Segmentation App

![PDX Segmentation App](docs/images/PDX_Segmentation_Home_Page.jpeg)

End-to-end imaging app: React frontend + FastAPI backend.

## Quick start (single Docker container)

Requirements:
- Docker installed (Docker Desktop on macOS/Windows)
- Optional GPU on Linux: NVIDIA drivers + NVIDIA Container Toolkit

Run:
```bash
./run.sh                    # CPU
GPU=1 ./run.sh              # GPU (Linux + NVIDIA)
```

What it does:
- Builds the React frontend and bundles it into the backend image
- Runs the FastAPI server at `http://localhost:8000`
- Serves the SPA from `/` and the API under the same origin
  (Ephemeral storage by default; data is not persisted outside the container)

Environment variables:
- `PORT` (default 8000 inside container; host maps to 8000)
- `PLATFORM_FLAG=--platform=linux/amd64` (if building on Apple Silicon and you need x86)

Notes:
- macOS/Windows run CPU-only. GPU mode requires Linux and NVIDIA toolkit.
- The image includes TensorFlow CPU by default; adjust as needed for your platform.

## First-time setup from GitHub

If you're cloning this repository on a new machine, follow these steps:

### Prerequisites
- **Git** installed
- **Python 3.11+** installed
- **Node.js 18+** and **npm** installed
- **Docker** (optional, for containerized deployment)

### Step 1: Clone the repository
```bash
git clone https://github.com/SatvikN/UCSF_PDX_Segmentation_App
cd UCSF_PDX_Segmentation_App
```

### Step 2: Download model weights
**⚠️ IMPORTANT**: The app requires pre-trained model weights to function.

1. **Download the model weights** from the release page or your storage location
2. **Place them in the correct directories**:
   ```bash
   # Create directories
   mkdir -p backend/app/models/segmentation_model/weights/
   mkdir -p backend/app/models/classifier_model/weights/
   
   # Copy your downloaded weights (replace paths with your actual files)
   cp /path/to/your/model_r2udensenet.hdf5 backend/app/models/segmentation_model/weights/
   cp /path/to/your/model_resnet50.hdf5 backend/app/models/classifier_model/weights/
   ```

### Step 3: Choose your deployment method

#### Option A: Docker (Recommended)

**From Docker Hub (if available):**
```bash
# Pull pre-built image
docker pull yourusername/pdx-seg-app:latest

# Run the container
docker run -p 8000:8000 yourusername/pdx-seg-app:latest
```

**Build from source:**
```bash
# Make run script executable
chmod +x run.sh

# Run with Docker
./run.sh                    # CPU
GPU=1 ./run.sh              # GPU (Linux + NVIDIA)
```

#### Option B: Local development
Follow the "Local development" section below.

### Step 4: Access the application
- **Web interface**: http://localhost:3000 (if using local development) or http://localhost:8000 (if using Docker)
- **API documentation**: http://localhost:8000/docs

## Local development (run frontend and backend separately)

Prerequisites:
- Node.js 18+ and npm
- Python 3.11

1) Backend
```bash
cd backend
python -m venv pdx-segmentation-env
source pdx-segmentation-env/bin/activate
pip install -r ../requirements-cpu.txt

# Run API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2) Frontend (in a second terminal)
```bash
cd frontend
npm install

# Point the frontend to the backend API (optional; defaults to http://localhost:8000)
export REACT_APP_SERVER_API_URL=http://localhost:8000

npm start
```

Frontend API base:
- The frontend uses `process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000'`.
- For production builds, set `REACT_APP_SERVER_API_URL` accordingly before `npm run build`.

## Project layout

```
backend/           # FastAPI app and ML models
frontend/          # React app (Create React App)
run.sh             # Build and run single-container image
Dockerfile         # Multi-stage build (frontend + backend)
.dockerignore
```

## Model Weights Setup

**⚠️ IMPORTANT**: The app requires pre-trained model weights to function.

### Download Model Weights

**Download Links**:
- [Weights for Classification and Segmentation Models](https://app.box.com/folder/340077806050)

### Setup Instructions

#### For Docker Container (Recommended)

If you're using the Docker container (`./run.sh`), the model weights are automatically included in the container image. **No additional setup required** - just run:

```bash
./run.sh                    # CPU
GPU=1 ./run.sh              # GPU (Linux + NVIDIA)
```

#### For Local Python Development

If you're running the code directly with Python (not Docker), follow these steps to place the model weights in the correct directories:

1. **Create the required directories** (if they don't exist):
   ```bash
   mkdir -p backend/app/models/segmentation_model/weights/
   mkdir -p backend/app/models/classifier_model/weights/
   ```

2. **Copy the segmentation model weights**:
   ```bash
   # Replace /path/to/your/model_r2udensenet.hdf5 with your actual file path
   cp /path/to/your/model_r2udensenet.hdf5 backend/app/models/segmentation_model/weights/model_r2udensenet.hdf5
   ```

3. **Copy the classifier model weights**:
   ```bash
   # Replace /path/to/your/model_resnet50.hdf5 with your actual file path
   cp /path/to/your/model_resnet50.hdf5 backend/app/models/classifier_model/weights/model_resnet50.hdf5
   ```

4. **Verify the files are in place**:
   ```bash
   ls -la backend/app/models/segmentation_model/weights/
   ls -la backend/app/models/classifier_model/weights/
   ```

   You should see:
   - `model_r2udensenet.hdf5` (~329MB) in the segmentation folder
   - `model_resnet50.hdf5` (~283MB) in the classifier folder

5. **Verify file types** (optional):
   ```bash
   file backend/app/models/segmentation_model/weights/model_r2udensenet.hdf5
   file backend/app/models/classifier_model/weights/model_resnet50.hdf5
   ```
   
   Both should show as "Hierarchical Data Format (HDF) data" or similar.

### Troubleshooting

- **If segmentation doesn't work**: Ensure the model weight files are actual binary HDF5 files
- **If you see "ASCII text" when checking file types**: The files are corrupted and need to be replaced with actual model weights
- **If files are too small** (< 1MB): The files are likely corrupted or incomplete
- **For Docker users**: Model weights are included in the container - no manual setup needed

## MATLAB Integration

The app supports exporting segmentation masks as MATLAB .mat files for further analysis in MATLAB.

### Downloading .mat Files

1. **Complete segmentation** on your DICOM images using the web interface
2. **Go to the Saving tab** in the web interface
3. **Click "Download masks only (MATLAB .mat)"** button
4. **File will be downloaded** as `masks.mat` (or with your custom prefix)

### Using .mat Files in MATLAB

```matlab
% Load the .mat file
load('masks.mat');

% The masks variable contains a 3D array
% Dimensions: (num_slices, height, width)
% Values: Binary mask (0 = background, 1 = tumor)

% Get basic information about the masks
fprintf('Number of slices: %d\n', size(masks, 1));
fprintf('Image dimensions: %d x %d\n', size(masks, 2), size(masks, 3));

% Access individual slice masks
slice1_mask = masks(1, :, :);  % First slice
slice5_mask = masks(5, :, :);  % Fifth slice

% Calculate total tumor volume (if you have pixel spacing and slice thickness)
% This requires additional metadata from the DICOM files
pixel_spacing_x = 0.5;  % mm (get from DICOM metadata)
pixel_spacing_y = 0.5;  % mm (get from DICOM metadata)
slice_thickness = 1.0;  % mm (get from DICOM metadata)

% Calculate volume for each slice
slice_volumes = zeros(size(masks, 1), 1);
for i = 1:size(masks, 1)
    slice_area_pixels = sum(masks(i, :, :), 'all');
    slice_area_mm2 = slice_area_pixels * pixel_spacing_x * pixel_spacing_y;
    slice_volumes(i) = slice_area_mm2 * slice_thickness / 1000;  % Convert to cc
end

total_volume_cc = sum(slice_volumes);
fprintf('Total tumor volume: %.2f cc\n', total_volume_cc);

% Visualize masks
figure;
for i = 1:min(6, size(masks, 1))  % Show first 6 slices
    subplot(2, 3, i);
    imshow(squeeze(masks(i, :, :)));
    title(sprintf('Slice %d', i));
end
```

### File Format Details

- **File extension**: `.mat`
- **Compression**: Yes (reduces file size)
- **Array name**: `masks`
- **Data type**: `uint8` (0 or 1)
- **Dimensions**: `(num_slices, height, width)`
- **Values**: 
  - `0` = Background/normal tissue
  - `1` = Tumor/segmented region

### Notes

- The .mat files contain only the binary mask arrays, not the original DICOM images
- For volume calculations, you'll need additional metadata (pixel spacing, slice thickness) from the original DICOM files
- The Excel export (`volumes.xlsx`) includes pre-calculated volumes with formulas you can modify

## Health check
API health endpoint: `GET /health` → `{ "status": "ok" }`
