import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { LottoBall, LoadingSpinner, ErrorMessage } from '../components';
import type { SystemStatus, LottoResult } from '../types';

export default function Home() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [latestResult, setLatestResult] = useState<LottoResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusRes, resultsRes] = await Promise.all([
        api.admin.status(),
        api.results.getAll({ page: 1, limit: 1 }),
      ]);
      setStatus(statusRes.data);
      if (resultsRes.data.results.length > 0) {
        setLatestResult(resultsRes.data.results[0]);
      }
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="데이터 로딩 중..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-4">로또 Machine Learning 예측 서비스</h1>
        <p className="text-blue-100 mb-6">
          머신러닝 기반 로또 번호 분석 및 예측 서비스입니다.
          <br />
          통계와 AI를 활용하여 번호를 분석해보세요.
        </p>
        <div className="flex space-x-4">
          <Link
            to="/predict"
            className="px-6 py-3 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
          >
            ML 예측 보기
          </Link>
          <Link
            to="/recommend"
            className="px-6 py-3 bg-blue-700 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            번호 추천 받기
          </Link>
        </div>
      </div>

      {/* Latest Result */}
      {latestResult && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">최신 당첨번호</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 mb-2">
                {latestResult.draw_no}회 ({latestResult.draw_date})
              </p>
              <div className="flex items-center space-x-2">
                {latestResult.numbers.map((num, idx) => (
                  <LottoBall key={idx} number={num} size="lg" />
                ))}
                <span className="text-2xl text-gray-400 mx-2">+</span>
                <LottoBall number={latestResult.bonus} size="lg" isBonus />
              </div>
            </div>
            <Link
              to="/results"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              전체 보기 →
            </Link>
          </div>
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">데이터베이스</h3>
          <p className="text-3xl font-bold text-blue-600">
            {status?.database.total_draws || 0}
          </p>
          <p className="text-gray-500 text-sm">총 회차 수</p>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">최신 회차</h3>
          <p className="text-3xl font-bold text-green-600">
            {status?.database.latest_draw || '-'}
          </p>
          <p className="text-gray-500 text-sm">{status?.database.latest_date || '-'}</p>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">ML 모델</h3>
          <p className="text-3xl font-bold text-purple-600">
            {status?.ml_models.trained ? '학습됨' : '미학습'}
          </p>
          <p className="text-gray-500 text-sm">
            {status?.ml_models.models_available.length || 0}개 모델
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          <strong>안내:</strong> 로또는 완전한 무작위 추첨이므로 AI/ML로 정확한 예측이
          불가능합니다. 본 서비스는 학습 및 오락 목적으로만 제공됩니다.
        </p>
      </div>
    </div>
  );
}
