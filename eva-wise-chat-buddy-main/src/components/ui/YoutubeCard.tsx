import React from 'react';

type YoutubeCardProps = {
  title: string;
  description: string;
  thumbnailUrl: string;
  videoUrl: string;
  channelTitle?: string;
};

const truncate = (text: string, max: number) =>
  text.length > max ? text.slice(0, max) + '...' : text;

export const YoutubeCard: React.FC<YoutubeCardProps> = ({
  title,
  description,
  thumbnailUrl,
  videoUrl,
  channelTitle,
}) => {
  const handleClick = () => {
    window.open(videoUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div
      className="mt-3 rounded-xl border border-white/10 bg-white/5 shadow-md overflow-hidden cursor-pointer hover:bg-white/10 transition-colors max-w-md"
      onClick={handleClick}
    >
      {thumbnailUrl && (
        <div className="w-full aspect-video overflow-hidden">
          <img
            src={thumbnailUrl}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <div className="p-3 space-y-1">
        <div className="inline-flex items-center gap-1 text-[11px] font-medium text-red-400 uppercase tracking-wide">
          🎥 فيديو شرح من يوتيوب
        </div>
        <div className="text-sm font-semibold line-clamp-2 text-gray-100 mt-1">
          {title}
        </div>
        {channelTitle && (
          <div className="text-[11px] text-gray-400">{channelTitle}</div>
        )}
        {description && (
          <p className="text-[11px] text-gray-300">
            {truncate(description, 140)}
          </p>
        )}
        <button
          type="button"
          className="mt-1 inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-red-600 text-white hover:bg-red-700"
        >
          شاهد الشرح على يوتيوب
        </button>
      </div>
    </div>
  );
};


