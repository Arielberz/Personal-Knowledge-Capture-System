const express = require("express");
const fs = require("fs");
const path = require("path");
const multer = require("multer");
const { processIncomingContent, uploadKnowledgeImage } = require("../controllers/knowledgeController");

const router = express.Router();
const uploadsDir = path.join(__dirname, "../../uploads");

fs.mkdirSync(uploadsDir, { recursive: true });

const storage = multer.diskStorage({
	destination: (req, file, cb) => {
		cb(null, uploadsDir);
	},
	filename: (req, file, cb) => {
		const ext = path.extname(file.originalname || "");
		cb(null, `${Date.now()}${ext}`);
	},
});

const upload = multer({ storage });

router.post("/api/knowledge", processIncomingContent);
router.post("/api/knowledge/upload", upload.single("image"), uploadKnowledgeImage);

module.exports = router;
