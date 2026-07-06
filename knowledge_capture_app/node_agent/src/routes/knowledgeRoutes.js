const express = require("express");
const { processIncomingContent } = require("../controllers/knowledgeController");

const router = express.Router();

router.post("/api/knowledge", async (req, res, next) => {
  try {
    const { rawText } = req.body ?? {};
    const data = await processIncomingContent(rawText);

    return res.status(200).json({
      ok: true,
      data,
    });
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
