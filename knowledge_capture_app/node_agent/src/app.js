const express = require("express");
const knowledgeRoutes = require("./routes/knowledgeRoutes");

const app = express();

app.use(express.json());
app.use(knowledgeRoutes);

app.use((error, req, res, next) => {
  const statusCode = Number.isInteger(error.statusCode) ? error.statusCode : 500;

  if (statusCode >= 500) {
    console.error("Knowledge API error:", error.message, error.cause || "");
  }

  return res.status(statusCode).json({
    ok: false,
    error: {
      message: statusCode === 500 ? "Internal server error." : error.message,
    },
  });
});

module.exports = app;
