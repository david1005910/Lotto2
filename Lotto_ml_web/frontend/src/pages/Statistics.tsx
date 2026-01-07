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
import type { Statistics } from '../types';

const COLORS = ['#FBC400', '#69C8F2', '#FF7272', '#AAAAAA', '#B0D840', '#9b59b6', '#1abc9c'];

export default function StatisticsPage() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recent, setRecent] = useState<number | undefined>(undefined);

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
  }, [recent]);

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
