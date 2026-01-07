import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LottoBall, LoadingSpinner, ErrorMessage } from '../components';
import type { RecommendData } from '../types';

const STRATEGY_NAMES: Record<string, string> = {
  high_frequency: '고빈도 번호',
  low_frequency: '저빈도 번호',
  balanced_odd_even: '홀짝 균형',
  section_spread: '구간 분산',
  optimal_sum: '합계 최적',
};

const STRATEGY_COLORS: Record<string, string> = {
  high_frequency: 'border-red-500 bg-red-50',
  low_frequency: 'border-blue-500 bg-blue-50',
  balanced_odd_even: 'border-green-500 bg-green-50',
  section_spread: 'border-yellow-500 bg-yellow-50',
  optimal_sum: 'border-purple-500 bg-purple-50',
};

const STRATEGY_ICONS: Record<string, string> = {
  high_frequency: '🔥',
  low_frequency: '❄️',
  balanced_odd_even: '⚖️',
  section_spread: '📊',
  optimal_sum: '🎯',
};

export default function Recommend() {
  const [recommend, setRecommend] = useState<RecommendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommend = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.recommend.get();
      setRecommend(response.data);
    } catch (err) {
      setError('추천 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommend();
  }, []);

  if (loading) return <LoadingSpinner message="번호 추천 생성 중..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchRecommend} />;
  if (!recommend) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">통계 기반 번호 추천</h1>
        <button
          onClick={fetchRecommend}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          새로 추천
        </button>
      </div>

      <p className="text-gray-600">
        다양한 통계 전략에 기반한 번호 조합을 추천합니다. 원하는 전략을 선택하세요.
      </p>

      {/* Recommendations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(recommend.recommendations).map(([strategyKey, data]) => (
          <div
            key={strategyKey}
            className={`rounded-xl border-2 p-6 transition-transform hover:scale-105 ${
              STRATEGY_COLORS[strategyKey] || 'border-gray-300 bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-2xl">{STRATEGY_ICONS[strategyKey] || '📌'}</span>
              <h2 className="text-lg font-bold">
                {STRATEGY_NAMES[strategyKey] || strategyKey}
              </h2>
            </div>
            <p className="text-sm text-gray-600 mb-4">{data.description}</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {data.numbers.map((num, idx) => (
                <LottoBall key={idx} number={num} size="lg" />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Strategy Explanations */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">전략 설명</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2">
              🔥 고빈도 번호
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              역대 출현 빈도가 높은 "핫 넘버"들을 조합합니다.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2">
              ❄️ 저빈도 번호
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              최근 출현하지 않은 "콜드 넘버"들을 조합합니다.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2">
              ⚖️ 홀짝 균형
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              홀수 3개, 짝수 3개로 균형 잡힌 조합입니다.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2">
              📊 구간 분산
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              저/중/고 구간에서 각 2개씩 균등하게 선택합니다.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg md:col-span-2">
            <h3 className="font-semibold flex items-center gap-2">
              🎯 합계 최적
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              6개 번호의 합이 130-150 범위가 되도록 조합합니다. (통계적으로 가장 많이 나오는 범위)
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          <strong>안내:</strong> 추천 번호는 통계적 분석에 기반하지만, 로또는 완전한 무작위 추첨이므로
          당첨을 보장하지 않습니다. 참고용으로만 사용해주세요.
        </p>
      </div>
    </div>
  );
}
