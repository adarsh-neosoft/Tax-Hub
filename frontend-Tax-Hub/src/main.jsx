import React from "react";
import ReactDOM from "react-dom/client";
import "./utils/setup-api.js";
import App from "./App";

import "iron-stack-ui/styles";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

 