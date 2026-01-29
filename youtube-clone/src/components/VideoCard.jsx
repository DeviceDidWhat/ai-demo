import React from 'react';

export default function VideoCard({ video }) {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-200">
      <div className="relative">
        <img
          src={video.thumbnail}
          alt={video.title}
          className="w-full h-48 object-cover"
        />
        <span className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
          {video.duration}
        </span>
      </div>
      <div className="p-3">
        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 text-sm">{video.title}</h3>
        <div className="flex items-center text-sm text-gray-600">
          <img
            src={video.channelAvatar}
            alt={video.channelName}
            className="w-6 h-6 rounded-full mr-2 border-2 border-gray-300"
          />
          <span className="font-medium text-xs">{video.channelName}</span>
        </div>
        <div className="text-sm text-gray-500 mt-1">
          <span className="text-xs">{video.views} views • {video.uploaded}</span>
        </div>
      </div>
    </div>
  );
}