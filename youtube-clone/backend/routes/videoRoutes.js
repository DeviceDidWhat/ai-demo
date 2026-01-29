import express from 'express';
import { uploadVideo, uploadImage } from '../utils/cloudinary.js';
import Video from '../models/Video.js';
import User from '../models/User.js';
import authenticate from '../middleware/auth.js';

const router = express.Router();

// Upload a new video
router.post('/upload', authenticate, uploadVideo.single('video'), uploadImage.single('thumbnail'), async (req, res) => {
  try {
    if (!req.files || !req.files.video || !req.files.thumbnail) {
      return res.status(400).json({ message: 'Video and thumbnail files are required' });
    }

    const { title, description, tags } = req.body;
    
    const newVideo = new Video({
      title,
      description,
      videoUrl: req.files.video[0].path,
      thumbnailUrl: req.files.thumbnail[0].path,
      uploadedBy: req.user.id,
      tags: tags ? tags.split(',') : []
    });

    await newVideo.save();
    res.status(201).json(newVideo);
  } catch (error) {
    console.error('Error uploading video:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get all videos
router.get('/', async (req, res) => {
  try {
    const videos = await Video.find()
      .populate('uploadedBy', 'username profilePicture')
      .sort({ createdAt: -1 });
    res.json(videos);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get video by ID
router.get('/:id', async (req, res) => {
  try {
    const video = await Video.findById(req.params.id)
      .populate('uploadedBy', 'username profilePicture')
      .populate('comments');
    
    if (!video) {
      return res.status(404).json({ message: 'Video not found' });
    }
    
    // Increment view count
    video.views += 1;
    await video.save();
    
    res.json(video);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Like a video
router.post('/:id/like', authenticate, async (req, res) => {
  try {
    const video = await Video.findById(req.params.id);
    
    if (!video) {
      return res.status(404).json({ message: 'Video not found' });
    }

    // Check if user already liked the video
    const userIndex = video.likes.indexOf(req.user.id);
    
    if (userIndex === -1) {
      // User hasn't liked yet, add like
      video.likes.push(req.user.id);
      
      // Remove from dislikes if present
      const dislikeIndex = video.dislikes.indexOf(req.user.id);
      if (dislikeIndex !== -1) {
        video.dislikes.splice(dislikeIndex, 1);
      }
    } else {
      // User already liked, remove like
      video.likes.splice(userIndex, 1);
    }

    await video.save();
    res.json(video);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Dislike a video
router.post('/:id/dislike', authenticate, async (req, res) => {
  try {
    const video = await Video.findById(req.params.id);
    
    if (!video) {
      return res.status(404).json({ message: 'Video not found' });
    }

    // Check if user already disliked the video
    const userIndex = video.dislikes.indexOf(req.user.id);
    
    if (userIndex === -1) {
      // User hasn't disliked yet, add dislike
      video.dislikes.push(req.user.id);
      
      // Remove from likes if present
      const likeIndex = video.likes.indexOf(req.user.id);
      if (likeIndex !== -1) {
        video.likes.splice(likeIndex, 1);
      }
    } else {
      // User already disliked, remove dislike
      video.dislikes.splice(userIndex, 1);
    }

    await video.save();
    res.json(video);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get videos by user
router.get('/user/:userId', async (req, res) => {
  try {
    const videos = await Video.find({ uploadedBy: req.params.userId })
      .populate('uploadedBy', 'username profilePicture')
      .sort({ createdAt: -1 });
    
    res.json(videos);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;