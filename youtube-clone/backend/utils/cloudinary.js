import { v2 as cloudinary } from 'cloudinary';
import { CloudinaryStorage } from 'multer-storage-cloudinary';
import multer from 'multer';

// Configure Cloudinary
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

// Set up storage for videos
const videoStorage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: 'youtube-clone/videos',
    resource_type: 'video',
    format: async (req, file) => 'mp4', // supports promises as well
    public_id: (req, file) => file.originalname.split('.')[0]
  }
});

// Set up storage for images (thumbnails, profile pictures)
const imageStorage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: 'youtube-clone/images',
    format: async (req, file) => 'jpg', // supports promises as well
    public_id: (req, file) => file.originalname.split('.')[0]
  }
});

// Create upload middlewares
const uploadVideo = multer({ storage: videoStorage });
const uploadImage = multer({ storage: imageStorage });

export { cloudinary, uploadVideo, uploadImage };