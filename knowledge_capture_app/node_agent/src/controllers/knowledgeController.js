const { GoogleGenAI, Type } = require("@google/genai");
const fs = require("fs");
const Knowledge = require("../../models/Knowledge");

const KNOWLEDGE_SCHEMA = {
  type: Type.OBJECT,
  additionalProperties: false,
  required: ["title", "summary", "tags", "category"],
  properties: {
    title: {
      type: Type.STRING,
      description: "A concise, catchy title for the content.",
    },
    summary: {
      type: Type.STRING,
      description: "A 2-3 sentence summary of the main points.",
    },
    tags: {
      type: Type.ARRAY,
      maxItems: 5,
      items: { type: Type.STRING },
      description: "Up to 5 relevant tags for categorization.",
    },
    category: {
      type: Type.STRING,
      description: "The primary category (e.g., Tech, Personal, Work, Ideas).",
    },
  },
};

async function generateStructuredContent(rawText) {
  if (typeof rawText !== "string" || rawText.trim().length === 0) {
    const error = new Error("rawText is required and must be a non-empty string.");
    error.statusCode = 400;
    throw error;
  }

  if (!process.env.GEMINI_API_KEY) {
    const error = new Error("GEMINI_API_KEY is missing.");
    error.statusCode = 500;
    throw error;
  }

  const ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY,
  });

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: rawText.trim(),
      config: {
        systemInstruction:
          "You are an expert knowledge management assistant. Analyze, organize, and structure incoming text into a clean JSON format.",
        responseMimeType: "application/json",
        responseSchema: KNOWLEDGE_SCHEMA,
      },
    });

    const result = JSON.parse(response.text);

    // Defensive normalization in case upstream output needs cleanup.
    result.tags = Array.isArray(result.tags)
      ? result.tags
          .filter((tag) => typeof tag === "string" && tag.trim().length > 0)
          .slice(0, 5)
      : [];

    return {
      title: typeof result.title === "string" ? result.title : "",
      summary: typeof result.summary === "string" ? result.summary : "",
      tags: result.tags,
      category: typeof result.category === "string" ? result.category : "",
    };
  } catch (cause) {
    const error = new Error("AI service failed to process incoming content.");
    error.statusCode = 502;
    error.cause = cause;
    throw error;
  }
}

async function processIncomingContent(req, res, next) {
  try {
    const { rawText } = req.body ?? {};
    const generated = await generateStructuredContent(rawText);

    const createdDocument = await Knowledge.create({
      rawContent: rawText.trim(),
      title: generated.title,
      summary: generated.summary,
      tags: generated.tags,
      category: generated.category,
    });

    return res.status(201).json({
      ok: true,
      data: createdDocument,
    });
  } catch (error) {
    if (error?.name === "ValidationError") {
      error.statusCode = 400;
    }

    return next(error);
  }
}

function normalizeTags(input) {
  if (Array.isArray(input)) {
    return input
      .map((tag) => (typeof tag === "string" ? tag.trim() : ""))
      .filter(Boolean);
  }

  if (typeof input === "string") {
    return input
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  return [];
}

async function uploadKnowledgeImage(req, res, next) {
  try {
    const { title, summary, tags, category } = req.body ?? {};

    if (!req.file) {
      const error = new Error("Image file is required.");
      error.statusCode = 400;
      throw error;
    }

    if (!process.env.GEMINI_API_KEY) {
      const error = new Error("GEMINI_API_KEY is missing.");
      error.statusCode = 500;
      throw error;
    }

    const ai = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
    });

    const imagePart = {
      inlineData: {
        data: fs.readFileSync(req.file.path).toString("base64"),
        mimeType: req.file.mimetype,
      },
    };

    const imageResponse = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: [
        {
          text:
            "Analyze this image and return structured JSON. Infer a useful primary category and tags based on what is visually present. For stock charts or market visuals, use a finance-related category and tags.",
        },
        imagePart,
      ],
      config: {
        systemInstruction:
          "You are an expert knowledge management assistant. Analyze images and structure them into a clean JSON format for indexing.",
        responseMimeType: "application/json",
        responseSchema: KNOWLEDGE_SCHEMA,
      },
    });

    const generated = JSON.parse(imageResponse.text);
    const generatedTags = normalizeTags(generated.tags).slice(0, 5);

    const imageUrl = `/uploads/${req.file.filename}`;
    const normalizedTags = normalizeTags(tags);

    const createdDocument = await Knowledge.create({
      // Keep compatibility with existing schema that requires rawContent.
      rawContent:
        [generated.title, generated.summary]
          .filter((value) => typeof value === "string" && value.trim())
          .join("\n") || req.file.originalname,
      title:
        typeof title === "string" && title.trim()
          ? title
          : typeof generated.title === "string"
            ? generated.title
            : req.file.originalname,
      summary:
        typeof summary === "string" && summary.trim()
          ? summary
          : typeof generated.summary === "string"
            ? generated.summary
            : "",
      tags: normalizedTags.length > 0 ? normalizedTags : generatedTags,
      category:
        typeof category === "string" && category.trim()
          ? category
          : typeof generated.category === "string"
            ? generated.category
            : "Uncategorized",
      imageUrl,
    });

    return res.status(201).json({
      ok: true,
      data: createdDocument,
    });
  } catch (error) {
    if (error?.name === "ValidationError") {
      error.statusCode = 400;
    }

    return next(error);
  }
}

module.exports = {
  processIncomingContent,
  generateStructuredContent,
  uploadKnowledgeImage,
};
