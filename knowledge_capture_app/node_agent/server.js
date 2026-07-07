require("dotenv").config();

const mongoose = require("mongoose");
const app = require("./src/app");

const port = Number.parseInt(process.env.PORT || "3000", 10);

if (!process.env.MONGO_URI) {
  console.error("MONGO_URI is missing.");
  process.exit(1);
}

mongoose
  .connect(process.env.MONGO_URI)
  .then(() => {
    app.listen(port, () => {
      console.log(`Knowledge API listening on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to connect to MongoDB:", error);
    process.exit(1);
  });
