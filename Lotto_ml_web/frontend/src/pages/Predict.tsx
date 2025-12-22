import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LottoBall, LoadingSpinner, ErrorMessage } from '../components';
import type { PredictionData } from '../types';

const MODEL_NAMES: Record<string, string> = {
  random_forest: 'Random Forest',
  gradient_boosting: 'Gradient Boosting',
  neural_network: 'Neural Network (MLP)',
};

const MODEL_COLORS: Record<string, string> = {
  random_forest: 'border-green-500 bg-green-50',
  gradient_boosting: 'border-blue-500 bg-blue-50',
  neural_network: 'border-purple-500 bg-purple-50',
};

export default function Predict() {
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.predict.get();
      setPrediction(response.data);
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        '예측 데이터를 불러오는데 실패했습니다. 먼저 모델을 학습해주세요.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, []);

  if (loading) return <LoadingSpinner message="예측 생성 중..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchPrediction} />;
  if (!prediction) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">ML 기반 번호 예측</h1>
        <button
          onClick={fetchPrediction}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          새로 예측
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">{prediction.disclaimer}</p>
      </div>

      {/* Last Trained Info */}
      {prediction.last_trained && (
        <p className="text-gray-500 text-sm">
          마지막 학습: {new Date(prediction.last_trained).toLocaleString('ko-KR')}
        </p>
      )}

      {/* Predictions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(prediction.predictions).map(([modelKey, data]) => (
          <div
            key={modelKey}
            className={`rounded-xl border-2 p-6 ${MODEL_COLORS[modelKey] || 'border-gray-300 bg-gray-50'}`}
          >
            <h2 className="text-lg font-bold mb-2">
              {MODEL_NAMES[modelKey] || modelKey}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              정확도: {(data.accuracy * 100).toFixed(1)}% (±3 범위)
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {data.numbers.map((num, idx) => (
                <LottoBall key={idx} number={num} size="lg" />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">모델 설명</h2>
        <div className="space-y-4 text-gray-600">
          <div>
            <h3 className="font-semibold text-gray-800">Random Forest</h3>
            <p className="text-sm">
              100개의 결정 트리를 앙상블하여 예측합니다. 과적합에 강하고 안정적입니다.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">Gradient Boosting</h3>
            <p className="text-sm">
              순차적으로 약한 학습기를 추가하여 오차를 줄입니다. 복잡한 패턴 학습에 유리합니다.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">Neural Network (MLP)</h3>
            <p className="text-sm">
              128-64-32 구조의 다층 퍼셉트론입니다. 비선형 관계를 학습할 수 있습니다.
            </p>
          </div>
        </div>
      </div>

      {/* Features Used */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">사용된 특성 (79개)</h2>
        <ul className="list-disc list-inside text-gray-600 space-y-1 text-sm">
          <li>이전 5회차 당첨번호 (30개)</li>
          <li>홀짝 비율, 고저 비율 (2개)</li>
          <li>평균, 표준편차 (2개)</li>
          <li>각 번호(1-45)의 최근 100회 출현 빈도 (45개)</li>
        </ul>
      </div>
    </div>
  );
}
