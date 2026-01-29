import express from 'express';
import Comment from '../models/Comment.js';
import Video from '../models/Video.js';
import authenticate from '../middleware/auth.js';

const router = express.Router();

// Add a comment to a video
router.post('/:videoId', authenticate, async (req, res) => {
  try {
    const { text } = req.body;
    const video = await Video.findById(req.params.videoId);
    
    if (!video) {
      return res.status(404).json({ message: 'Video not found' });
    }
    
    const newComment = new Comment({
      text,
      videoId: req.params.videoId,
      userId: req.user.id
    });
    
    await newComment.save();
    
    // Add comment to video
    video.comments.push(newComment._id);
    await video.save();
    
    // Populate user data
    const comment = await Comment.findById(newComment._id)
      .populate('userId', 'username profilePicture');
    
    res.status(201).json(comment);
  } catch (error) {
    console.error('Error adding comment:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get all comments for a video
router.get('/:videoId', async (req, res) => {
  try {
    const comments = await Comment.find({ videoId: req.params.videoId })
      .populate('userId', 'username profilePicture')
      .populate({
        path: 'replies',
        populate: {
          path: 'userId',
          select: 'username profilePicture'
        }
      })
      .sort({ createdAt: -1 });
    
    res.json(comments);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Like a comment
router.post('/:commentId/like', authenticate, async (req, res) => {
  try {
    const comment = await Comment.findById(req.params.commentId);
    
    if (!comment) {
      return res.status(404).json({ message: 'Comment not found' });
    }
    
    // Check if user already liked the comment
    const userIndex = comment.likes.indexOf(req.user.id);
    
    if (userIndex === -1) {
      // User hasn't liked yet, add like
      comment.likes.push(req.user.id);
    } else {
      // User already liked, remove like
      comment.likes.splice(userIndex, 1);
    }
    
    await comment.save();
    res.json(comment);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Reply to a comment
router.post('/:commentId/reply', authenticate, async (req, res) => {
  try {
    const { text } = req.body;
    const parentComment = await Comment.findById(req.params.commentId);
    
    if (!parentComment) {
      return res.status(404).json({ message: 'Parent comment not found' });
    }
    
    const newReply = new Comment({
      text,
      videoId: parentComment.videoId,
      userId: req.user.id
    });
    
    await newReply.save();
    
    // Add reply to parent comment
    parentComment.replies.push(newReply._id);
    await parentComment.save();
    
    // Populate user data
    const reply = await Comment.findById(newReply._id)
      .populate('userId', 'username profilePicture');
    
    res.status(201).json(reply);
  } catch (error) {
    console.error('Error adding reply:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete a comment
router.delete('/:commentId', authenticate, async (req, res) => {
  try {
    const comment = await Comment.findById(req.params.commentId);
    
    if (!comment) {
      return res.status(404).json({ message: 'Comment not found' });
    }
    
    // Check if user owns the comment
    if (comment.userId.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to delete this comment' });
    }
    
    // Remove comment from video
    const video = await Video.findById(comment.videoId);
    if (video) {
      const commentIndex = video.comments.indexOf(comment._id);
      if (commentIndex !== -1) {
        video.comments.splice(commentIndex, 1);
        await video.save();
      }
    }
    
    // Remove the comment
    await Comment.findByIdAndDelete(req.params.commentId);
    
    res.json({ message: 'Comment deleted successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;