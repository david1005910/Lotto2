import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', label: '홈' },
  { path: '/results', label: '당첨번호' },
  { path: '/statistics', label: '통계' },
  { path: '/predict', label: 'ML 예측' },
  { path: '/recommend', label: '추천' },
  { path: '/admin', label: '관리' },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold">
            로또 Machine Learning 예측
          </Link>
          <div className="flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  px-4 py-2 rounded-md text-sm font-medium
                  transition-colors duration-200
                  ${
                    location.pathname === item.path
                      ? 'bg-blue-700 text-white'
                      : 'text-blue-100 hover:bg-blue-500'
                  }
                `}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
