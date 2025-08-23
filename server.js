// server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

mongoose.connect('mongodb://localhost:27017/phmart', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const User = mongoose.model('User', new mongoose.Schema({
  email: String,
  mobile: String,
  username: String,
  password: String
}));

app.post('/api/register', async (req, res) => {
  const { email, mobile, username, password } = req.body;
  const exists = await User.findOne({ username });

  if (exists) return res.status(400).json({ message: "Username already exists" });

  await new User({ email, mobile, username, password }).save();
  res.json({ message: "User registered" });
});

app.listen(5000, () => console.log("Server started on http://localhost:5000"));
