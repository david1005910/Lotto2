import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { LoadingSpinner, ErrorMessage } from '../components';
import type { Statistics, SimulationData, SimulationInfo } from '../types';

const COLORS = ['#FBC400', '#69C8F2', '#FF7272', '#AAAAAA', '#B0D840', '#9b59b6', '#1abc9c'];

export default function StatisticsPage() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recent, setRecent] = useState<number | undefined>(undefined);

  // Simulation states
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null);
  const [simulationInfo, setSimulationInfo] = useState<SimulationInfo | null>(null);
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [numPredictions, setNumPredictions] = useState(1000);
  const [progress, setProgress] = useState(0);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.statistics.get(recent);
      setStats(response.data);
    } catch (err) {
      setError('통계 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchSimulationInfo();
  }, [recent]);

  const fetchSimulationInfo = async () => {
    try {
      const response = await api.simulation.info();
      setSimulationInfo(response.data);
    } catch (err) {
      console.warn('Simulation info not available:', err);
    }
  };

  const runSimulation = async () => {
    setSimulationLoading(true);
    setSimulationError(null);
    setProgress(0);

    try {
      // Start progress animation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 5;
        });
      }, 200);

      const response = await api.simulation.run(numPredictions);

      clearInterval(progressInterval);
      setProgress(100);
      setSimulationData(response.data);

      // Reset progress after a short delay
      setTimeout(() => setProgress(0), 1000);
    } catch (err: any) {
      setSimulationError(err.response?.data?.detail || '시뮬레이션 실행 중 오류가 발생했습니다.');
    } finally {
      setSimulationLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="통계 계산 중..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchStats} />;
  if (!stats) return null;

  // Prepare frequency data
  const frequencyData = Object.entries(stats.number_frequency)
    .map(([num, count]) => ({
      number: parseInt(num),
      count,
    }))
    .sort((a, b) => a.number - b.number);

  // Prepare odd/even data
  const oddEvenData = Object.entries(stats.odd_even_distribution).map(([key, value]) => ({
    name: key.replace('_odd', '홀'),
    value,
  }));

  // Prepare sum distribution data
  const sumData = stats.sum_distribution.ranges.map((range, idx) => ({
    range,
    count: stats.sum_distribution.counts[idx],
  }));

  // Prepare consecutive data
  const consecutiveData = [
    { name: '연속번호 있음', value: stats.consecutive_stats.has_consecutive },
    { name: '연속번호 없음', value: stats.consecutive_stats.no_consecutive },
  ];

  // Prepare simulation results data
  const simulationResultsData = simulationData ? [
    { rank: '1등', name: '6개 일치', count: simulationData.winner_stats['1st_place'].count, percentage: simulationData.winner_stats['1st_place'].percentage },
    { rank: '2등', name: '5개+보너스', count: simulationData.winner_stats['2nd_place'].count, percentage: simulationData.winner_stats['2nd_place'].percentage },
    { rank: '3등', name: '5개 일치', count: simulationData.winner_stats['3rd_place'].count, percentage: simulationData.winner_stats['3rd_place'].percentage },
    { rank: '4등', name: '4개 일치', count: simulationData.winner_stats['4th_place'].count, percentage: simulationData.winner_stats['4th_place'].percentage },
    { rank: '5등', name: '3개 일치', count: simulationData.winner_stats['5th_place'].count, percentage: simulationData.winner_stats['5th_place'].percentage },
  ] : [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">통계 분석</h1>
        <div className="flex items-center space-x-2">
          <span className="text-gray-600">기간:</span>
          <select
            value={recent || ''}
            onChange={(e) => setRecent(e.target.value ? parseInt(e.target.value) : undefined)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">전체</option>
            <option value="10">최근 10회</option>
            <option value="50">최근 50회</option>
            <option value="100">최근 100회</option>
            <option value="500">최근 500회</option>
          </select>
        </div>
      </div>

      <p className="text-gray-600">분석 대상: {stats.total_draws}회</p>

      {/* Prediction Simulation Section */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">예측 성능 시뮬레이션</h2>
          {simulationInfo && (
            <div className="text-sm text-gray-600">
              기준: {simulationInfo.latest_draw.draw_no}회 ({simulationInfo.latest_draw.draw_date})
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                시뮬레이션 횟수
              </label>
              <select
                value={numPredictions}
                onChange={(e) => setNumPredictions(parseInt(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={simulationLoading}
              >
                <option value={1000}>1,000회</option>
                <option value={10000}>1만회</option>
                <option value={100000}>10만회</option>
                <option value={1000000}>100만회</option>
                <option value={10000000}>1,000만회</option>
                <option value={50000000}>5,000만회</option>
                <option value={100000000}>1억회</option>
              </select>
            </div>

            <button
              onClick={runSimulation}
              disabled={simulationLoading || !simulationInfo}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {simulationLoading ? '시뮬레이션 중...' : '시뮬레이션 실행'}
            </button>

            {numPredictions >= 10000000 && (
              <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
                <p className="font-medium mb-1">⚠️ 대용량 시뮬레이션 안내</p>
                <p>{numPredictions.toLocaleString()}회 시뮬레이션은 {Math.ceil(numPredictions / 1000000)}분 이상 소요될 수 있습니다.</p>
              </div>
            )}

            {simulationLoading && progress > 0 && (
              <div className="w-full">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>진행률</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {simulationError && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                {simulationError}
              </div>
            )}

            {simulationInfo && (
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                <p className="font-medium mb-1">기준 당첨번호</p>
                <div className="flex flex-wrap gap-1 mb-2">
                  {simulationInfo.latest_draw.winning_numbers.map((num, idx) => (
                    <span key={idx} className="inline-flex items-center justify-center w-6 h-6 text-xs bg-blue-100 text-blue-800 rounded-full">
                      {num}
                    </span>
                  ))}
                  <span className="inline-flex items-center justify-center w-6 h-6 text-xs bg-red-100 text-red-800 rounded-full border-2 border-red-200">
                    {simulationInfo.latest_draw.bonus_number}
                  </span>
                </div>
                <p className="text-xs">{simulationInfo.description}</p>
              </div>
            )}
          </div>

          {/* Results Chart */}
          {simulationData && (
            <div className="lg:col-span-2">
              <h3 className="font-medium mb-4">등수별 당첨 결과 ({simulationData.total_predictions.toLocaleString()}회)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={simulationResultsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="rank" />
                  <YAxis />
                  <Tooltip
                    formatter={(value, name) => [
                      name === 'count' ? `${value}개` : `${value}%`,
                      name === 'count' ? '당첨 개수' : '당첨률'
                    ]}
                    labelFormatter={(label) => `${label} 당첨`}
                  />
                  <Bar dataKey="count" fill="#3B82F6" name="count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Results Table */}
        {simulationData && (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left font-medium text-gray-700">등수</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">조건</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">당첨 개수</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">당첨률</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {simulationResultsData.map((result) => (
                  <tr key={result.rank} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{result.rank}</td>
                    <td className="px-4 py-3 text-gray-600">{result.name}</td>
                    <td className="px-4 py-3 text-right font-mono">{result.count.toLocaleString()}개</td>
                    <td className="px-4 py-3 text-right font-mono">{result.percentage}%</td>
                  </tr>
                ))}
                <tr className="bg-gray-50 font-medium">
                  <td className="px-4 py-3">미당첨</td>
                  <td className="px-4 py-3 text-gray-600">2개 이하 일치</td>
                  <td className="px-4 py-3 text-right font-mono">{simulationData.winner_stats.no_prize.count.toLocaleString()}개</td>
                  <td className="px-4 py-3 text-right font-mono">{simulationData.winner_stats.no_prize.percentage}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Number Frequency Chart */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">번호별 출현 빈도</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={frequencyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="number" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="count"
              fill="#3B82F6"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Odd/Even Distribution */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">홀짝 분포</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={oddEvenData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                }
              >
                {oddEvenData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Consecutive Stats */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">연속번호 통계</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={consecutiveData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                }
              >
                <Cell fill="#3B82F6" />
                <Cell fill="#E5E7EB" />
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sum Distribution */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">합계 분포</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sumData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Section Distribution */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">구간별 평균 출현 수</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-lotto-yellow/20 rounded-lg">
            <p className="text-lg font-bold">저번호 (1-15)</p>
            <p className="text-3xl font-bold text-lotto-yellow">
              {stats.section_distribution.low_1_15.avg}
            </p>
            <p className="text-gray-500">평균 개수</p>
          </div>
          <div className="text-center p-4 bg-lotto-red/20 rounded-lg">
            <p className="text-lg font-bold">중번호 (16-30)</p>
            <p className="text-3xl font-bold text-lotto-red">
              {stats.section_distribution.mid_16_30.avg}
            </p>
            <p className="text-gray-500">평균 개수</p>
          </div>
          <div className="text-center p-4 bg-lotto-green/20 rounded-lg">
            <p className="text-lg font-bold">고번호 (31-45)</p>
            <p className="text-3xl font-bold text-lotto-green">
              {stats.section_distribution.high_31_45.avg}
            </p>
            <p className="text-gray-500">평균 개수</p>
          </div>
        </div>
      </div>
    </div>
  );
}
