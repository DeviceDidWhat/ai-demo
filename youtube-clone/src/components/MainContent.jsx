import React from 'react';
import VideoCard from './VideoCard';

export default function MainContent() {
  const videos = [
    {
      id: 1,
      title: 'Learn React in 1 Hour',
      thumbnail: 'https://via.placeholder.com/320x180/4285F4/FFFFFF?text=React',
      duration: '12:34',
      channelName: 'Web Dev Tutorials',
      channelAvatar: 'https://i.pravatar.cc/40?u=webdev',
      views: '1.2M',
      uploaded: '2 weeks ago'
    },
    {
      id: 2,
      title: 'Advanced JavaScript Techniques',
      thumbnail: 'https://via.placeholder.com/320x180/F7DF1E/000000?text=JS',
      duration: '25:18',
      channelName: 'Code Masters',
      channelAvatar: 'https://i.pravatar.cc/40?u=codemasters',
      views: '850K',
      uploaded: '1 month ago'
    },
    {
      id: 3,
      title: 'CSS Grid Layout Tutorial',
      thumbnail: 'https://via.placeholder.com/320x180/264DE4/FFFFFF?text=CSS',
      duration: '18:45',
      channelName: 'Frontend Experts',
      channelAvatar: 'https://i.pravatar.cc/40?u=frontend',
      views: '620K',
      uploaded: '3 weeks ago'
    },
    {
      id: 4,
      title: 'Node.js Crash Course',
      thumbnail: 'https://via.placeholder.com/320x180/68A063/FFFFFF?text=Node',
      duration: '32:10',
      channelName: 'Backend Basics',
      channelAvatar: 'https://i.pravatar.cc/40?u=backend',
      views: '1.5M',
      uploaded: '1 month ago'
    },
    {
      id: 5,
      title: 'Python for Beginners',
      thumbnail: 'https://via.placeholder.com/320x180/3776AB/FFFFFF?text=Python',
      duration: '45:22',
      channelName: 'Programming 101',
      channelAvatar: 'https://i.pravatar.cc/40?u=programming',
      views: '2.1M',
      uploaded: '2 months ago'
    },
    {
      id: 6,
      title: 'Machine Learning Basics',
      thumbnail: 'https://via.placeholder.com/320x180/FF9800/FFFFFF?text=ML',
      duration: '58:30',
      channelName: 'AI Academy',
      channelAvatar: 'https://i.pravatar.cc/40?u=aiacademy',
      views: '950K',
      uploaded: '3 months ago'
    },
  ];

  return (
    <main className="flex-1 p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {videos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </main>
  );
}