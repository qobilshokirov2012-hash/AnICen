require("dotenv").config();

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const axios = require("axios");

const app = express();

app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URL)
.then(() => console.log("MongoDB connected"))
.catch(err => console.log(err));

const AnimeSchema = new mongoose.Schema({
  title: String,
  image: String,
  description: String
});

const Anime = mongoose.model("Anime", AnimeSchema);

app.get("/", (req, res) => {
  res.send("AnICen Uz API working 🚀");
});

app.get("/anime/:name", async (req, res) => {

  try {

    const anime = await Anime.findOne({
      title: new RegExp(req.params.name, "i")
    });

    if (!anime) {
      return res.json({
        success: false,
        message: "Anime topilmadi"
      });
    }

    res.json({
      success: true,
      anime
    });

  } catch (err) {

    res.status(500).json({
      success: false,
      error: err.message
    });

  }

});

app.post("/ai", async (req, res) => {

  try {

    const message = req.body.message;

    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        contents: [
          {
            parts: [
              {
                text:
                  `You are AnICen Uz AI anime assistant. Reply like anime expert.\nUser: ${message}`
              }
            ]
          }
        ]
      }
    );

    const reply =
      response.data.candidates[0].content.parts[0].text;

    res.json({
      success: true,
      reply
    });

  } catch (err) {

    res.status(500).json({
      success: false,
      error: err.message
    });

  }

});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Server running 🚀");
});
