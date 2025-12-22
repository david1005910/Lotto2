interface LottoBallProps {
  number: number;
  size?: 'sm' | 'md' | 'lg';
  isBonus?: boolean;
}

const getBallColor = (num: number): string => {
  if (num <= 10) return 'bg-lotto-yellow';
  if (num <= 20) return 'bg-lotto-blue';
  if (num <= 30) return 'bg-lotto-red';
  if (num <= 40) return 'bg-lotto-gray';
  return 'bg-lotto-green';
};

const getSizeClass = (size: 'sm' | 'md' | 'lg'): string => {
  switch (size) {
    case 'sm':
      return 'w-8 h-8 text-sm';
    case 'lg':
      return 'w-14 h-14 text-xl';
    default:
      return 'w-10 h-10 text-base';
  }
};

export default function LottoBall({
  number,
  size = 'md',
  isBonus = false,
}: LottoBallProps) {
  return (
    <div
      className={`
        ${getBallColor(number)}
        ${getSizeClass(size)}
        ${isBonus ? 'ring-2 ring-purple-500 ring-offset-2' : ''}
        rounded-full flex items-center justify-center
        text-white font-bold shadow-md
        transition-transform hover:scale-110
      `}
    >
      {number}
    </div>
  );
}
