const { GoogleGenAI, Type } = require("@google/genai");

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

async function processIncomingContent(rawText) {
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

module.exports = {
  processIncomingContent,
};
