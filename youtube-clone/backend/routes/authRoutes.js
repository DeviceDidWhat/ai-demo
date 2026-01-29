import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import User from '../models/User.js';
import { uploadImage } from '../utils/cloudinary.js';
import authenticate from '../middleware/auth.js';

const router = express.Router();

// Register a new user
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // Check if user already exists
    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(400).json({ message: 'User with this email or username already exists' });
    }
    
    // Create new user
    const newUser = new User({ username, email, password });
    await newUser.save();
    
    // Generate token
    const token = jwt.sign({ id: newUser._id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    
    res.status(201).json({
      token,
      user: {
        id: newUser._id,
        username: newUser.username,
        email: newUser.email,
        profilePicture: newUser.profilePicture
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Login user
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user by email
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    // Check password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    // Generate token
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    
    res.json({
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        profilePicture: user.profilePicture
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get current user
router.get('/me', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update user profile
router.put('/me', authenticate, uploadImage.single('profilePicture'), async (req, res) => {
  try {
    const { username, email } = req.body;
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Update fields
    if (username) user.username = username;
    if (email) user.email = email;
    if (req.file) user.profilePicture = req.file.path;
    
    await user.save();
    
    res.json({
      id: user._id,
      username: user.username,
      email: user.email,
      profilePicture: user.profilePicture
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Subscribe to a channel
router.post('/subscribe/:channelId', authenticate, async (req, res) => {
  try {
    const channel = await User.findById(req.params.channelId);
    const currentUser = await User.findById(req.user.id);
    
    if (!channel || !currentUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Check if already subscribed
    if (currentUser.subscribedChannels.includes(channel._id)) {
      return res.status(400).json({ message: 'Already subscribed to this channel' });
    }
    
    // Add to subscriptions
    currentUser.subscribedChannels.push(channel._id);
    channel.subscribers.push(currentUser._id);
    
    await currentUser.save();
    await channel.save();
    
    res.json({ message: 'Subscribed successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Unsubscribe from a channel
router.post('/unsubscribe/:channelId', authenticate, async (req, res) => {
  try {
    const channel = await User.findById(req.params.channelId);
    const currentUser = await User.findById(req.user.id);
    
    if (!channel || !currentUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Check if subscribed
    const subIndex = currentUser.subscribedChannels.indexOf(channel._id);
    if (subIndex === -1) {
      return res.status(400).json({ message: 'Not subscribed to this channel' });
    }
    
    // Remove from subscriptions
    currentUser.subscribedChannels.splice(subIndex, 1);
    const channelIndex = channel.subscribers.indexOf(currentUser._id);
    channel.subscribers.splice(channelIndex, 1);
    
    await currentUser.save();
    await channel.save();
    
    res.json({ message: 'Unsubscribed successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;