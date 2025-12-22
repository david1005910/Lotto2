import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LoadingSpinner, ErrorMessage } from '../components';
import type { SystemStatus } from '../types';

export default function Admin() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.admin.status();
      setStatus(response.data);
    } catch (err) {
      setError('상태 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async (full: boolean = false) => {
    setSyncing(true);
    setMessage(null);
    try {
      const response = full
        ? await api.admin.syncFull()
        : await api.admin.sync();
      setMessage(`${response.data.synced_count}개 회차 동기화 완료`);
      fetchStatus();
    } catch (err) {
      setMessage('동기화 중 오류가 발생했습니다.');
    } finally {
      setSyncing(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    setMessage(null);
    try {
      const response = await api.admin.train();
      const modelCount = Object.keys(response.data.models).length;
      setMessage(`${modelCount}개 모델 학습 완료`);
      fetchStatus();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '모델 학습 중 오류가 발생했습니다.';
      setMessage(errorMsg);
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchStatus} />;
  if (!status) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">시스템 관리</h1>

      {/* Status Message */}
      {message && (
        <div
          className={`p-4 rounded-lg ${
            message.includes('오류') || message.includes('실패')
              ? 'bg-red-100 text-red-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {message}
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database Status */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">데이터베이스 상태</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">총 회차 수</span>
              <span className="font-semibold">{status.database.total_draws}회</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">최신 회차</span>
              <span className="font-semibold">{status.database.latest_draw || '-'}회</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">최신 추첨일</span>
              <span className="font-semibold">{status.database.latest_date || '-'}</span>
            </div>
          </div>
        </div>

        {/* ML Model Status */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">ML 모델 상태</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">학습 상태</span>
              <span
                className={`font-semibold ${
                  status.ml_models.trained ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {status.ml_models.trained ? '학습됨' : '미학습'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">마지막 학습</span>
              <span className="font-semibold">
                {status.ml_models.last_trained
                  ? new Date(status.ml_models.last_trained).toLocaleString('ko-KR')
                  : '-'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">사용 가능 모델</span>
              <span className="font-semibold">
                {status.ml_models.models_available.length}개
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">작업</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">증분 동기화</h3>
            <p className="text-sm text-gray-600 mb-4">
              새로운 회차만 동기화합니다.
            </p>
            <button
              onClick={() => handleSync(false)}
              disabled={syncing}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {syncing ? '동기화 중...' : '증분 동기화'}
            </button>
          </div>
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">전체 동기화</h3>
            <p className="text-sm text-gray-600 mb-4">
              1회차부터 전체를 동기화합니다.
            </p>
            <button
              onClick={() => handleSync(true)}
              disabled={syncing}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {syncing ? '동기화 중...' : '전체 동기화'}
            </button>
          </div>
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">모델 학습</h3>
            <p className="text-sm text-gray-600 mb-4">
              ML 모델을 학습시킵니다.
            </p>
            <button
              onClick={handleTrain}
              disabled={training || status.database.total_draws < 10}
              className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {training ? '학습 중...' : '모델 학습'}
            </button>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-2">사용 방법</h3>
        <ol className="list-decimal list-inside text-blue-700 text-sm space-y-1">
          <li>먼저 "전체 동기화"를 클릭하여 당첨번호 데이터를 수집합니다.</li>
          <li>데이터 수집이 완료되면 "모델 학습"을 클릭합니다.</li>
          <li>학습이 완료되면 "ML 예측" 페이지에서 예측 결과를 확인할 수 있습니다.</li>
          <li>새로운 회차가 추첨되면 "증분 동기화"로 업데이트하세요.</li>
        </ol>
      </div>
    </div>
  );
}
