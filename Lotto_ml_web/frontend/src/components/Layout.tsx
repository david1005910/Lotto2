import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="bg-gray-800 text-white text-center py-4 mt-8">
        <p className="text-sm">
          로또 Machine Learning 예측 서비스 - 본 서비스는 참고용이며 당첨을 보장하지 않습니다.
        </p>
      </footer>
    </div>
  );
}
