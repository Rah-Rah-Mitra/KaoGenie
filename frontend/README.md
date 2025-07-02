# SmartExam - Frontend Application

This directory contains the React + Vite frontend for the SmartExam project. It provides the user interface for generating exams and displays the real-time progress and final results from the backend API.

> **Note:** This frontend requires the backend service to be running. For full project setup, please refer to the [main README.md](../README.md) at the root of the project.

## Getting Started

To run the frontend application for development, follow these steps from the `frontend` directory:

1.  **Ensure you have Node.js and npm installed** (v18.x or higher is recommended).

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Run the development server:**
    The application will be available at `http://localhost:5173`.
    ```sh
    npm run dev
    ```

## Available Scripts

-   **`npm run dev`**: Runs the app in development mode with hot-reloading.
-   **`npm run build`**: Bundles the app for production into the `dist` folder.
-   **`npm run preview`**: Serves the production build locally to preview it.

## Key Technologies

-   **Framework:** React with TypeScript
-   **Build Tool:** Vite
-   **Styling:** Tailwind CSS (with JIT compilation and dark mode support)
-   **API Communication:** Uses the native `fetch` API to communicate with the backend via Server-Sent Events (SSE) for live progress.

## Project Structure

-   `/src/components`: Contains all reusable React components.
-   `/src/services`: Includes the `apiService.ts` file responsible for all backend communication.
-   `/src/App.tsx`: The main application component that manages state and views.
-   `/src/constants.ts`: Stores constants like the backend API URL.