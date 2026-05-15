require("dotenv").config();

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

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

});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Server running");
});
