const mongoose = require("mongoose");

const { Schema } = mongoose;

const KnowledgeSchema = new Schema(
  {
    rawContent: {
      type: String,
      required: true,
      trim: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    summary: {
      type: String,
      required: true,
      trim: true,
    },
    tags: {
      type: [String],
      default: [],
    },
    category: {
      type: String,
      required: true,
      trim: true,
    },
    imageUrl: {
      type: String,
      trim: true,
      default: null,
    },
    createdAt: {
      type: Date,
      default: Date.now,
    },
  },
  {
    versionKey: false,
  }
);

KnowledgeSchema.index({ title: "text", summary: "text", rawContent: "text" });

module.exports = mongoose.models.Knowledge || mongoose.model("Knowledge", KnowledgeSchema);
