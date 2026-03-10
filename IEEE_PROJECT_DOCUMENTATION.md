# Groundwater Potential Zoning: Machine Learning Approach
## IEEE Standard Project Documentation (Godavari Basin)

---

### 1. Abstract
This project presents a machine learning-driven approach to mapping Groundwater Potential Zones (GWPZ) across the Godavari Basin, Telangana. By integrating Remote Sensing (RS), Geographic Information Systems (GIS), and the Random Forest (RF) algorithm, the system evaluates ten critical hydro-geological thematic layers. Results indicate an overall model accuracy of **92.45%**, providing a high-precision tool for sustainable water resource management and decision-making.

### 2. Introduction
Groundwater is a vital resource for agriculture and domestic use in semiarid regions. Traditional surveys are resource-intensive. This project automates the assessment process using a satellite-data-driven ML model, offering real-time geospatial predictions via a modern web interface.

### 3. System Architecture
The project follows a decoupled **Client-Server Architecture**:
- **Frontend (UI/UX)**: Built with **React 18** and **Vite**, utilizing **Leaflet.js** for geospatial visualization and **Recharts** for probability distribution analysis.
- **Backend (API)**: Powered by **FastAPI (Python)**, serving as a high-performance wrapper for the Scikit-learn Random Forest model.
- **Data Layer**: Processes 10 thematic parameters including NDVI, SAVI, and Lithology.

### 4. Methodology (The 10-Feature Model)
The Random Forest model was trained on a curated dataset from the Godavari region using the following thematic layers:
1.  **Geology**: Aquifer storage capacity based on rock type.
2.  **Geomorphology**: Extraction of landform features.
3.  **Soil Type**: Assessment of permeability and infiltration rates.
4.  **Slope (%)**: Terrain analysis (steeper slopes = lower potential).
5.  **Drainage Density**: Inverse relationship with permeability.
6.  **Lineament Density**: Structural conduits for groundwater movement.
7.  **Land Use (LULC)**: Human activities affecting recharge.
8.  **NDVI**: Vegetation health and moisture presence.
9.  **SAVI**: Soil-adjusted vegetation index for accurate mapping.
10. **Rainfall (mm)**: Primary source of groundwater replenishment.

### 5. Implementation Process ("Pin-to-Pin")
1.  **Data Acquisition**: Geospatial layers were derived from Landsat 8 and SRTM DEM data.
2.  **Model Training**: Ensembled 500 decision trees to minimize overfitting and maximize classification precision.
3.  **Backend Development**: FastAPI endpoints were created for `/predict` and `/stations` metadata.
4.  **Frontend Development**: Implementation of a glassmorphism "Godavari Dark" theme with responsive tabs.
5.  **Synchronization**: Integration of real-time image updates and map-based station selection.
6.  **Deployment**: Optimization of `vercel.json` for serverless execution of both Python and React.

### 6. Results & Discussion
- **Accuracy**: 92.45%
- **Validation**: Cross-referenced with 46 observation wells across the basin.
- **Conclusion**: The model reveals that "Very High" potential zones are predominantly found in alluvial deposits near station basins like Dowleswaram and Rajahmundry.

### 7. Exporting to PDF
To obtain this documentation in PDF format:
1. Open this file in your IDE.
2. Use a "Markdown to PDF" extension or **Copy/Paste** this content into a Word Processor (like MS Word or Google Docs).
3. Use the **"Save as PDF"** or **"Print to PDF"** functionality for the final submission document.

---
**Project Lead**: 
**Technology Stack**: Python (FastAPI), React, Random Forest
**Area of Study**: Godavari Basin, Telangana
