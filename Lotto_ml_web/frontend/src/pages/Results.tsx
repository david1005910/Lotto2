import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LottoBall, LoadingSpinner, ErrorMessage } from '../components';
import type { LottoResult, Pagination } from '../types';

export default function Results() {
  const [results, setResults] = useState<LottoResult[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [searchDraw, setSearchDraw] = useState('');

  const fetchResults = async (pageNum: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.results.getAll({ page: pageNum, limit: 20 });
      setResults(response.data.results);
      setPagination(response.data.pagination);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchDraw) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.results.getByDrawNo(parseInt(searchDraw));
      setResults([response.data]);
      setPagination(null);
    } catch (err) {
      setError(`${searchDraw}회차를 찾을 수 없습니다.`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const resetSearch = () => {
    setSearchDraw('');
    setPage(1);
    fetchResults(1);
  };

  useEffect(() => {
    fetchResults(page);
  }, [page]);

  const formatPrize = (prize?: number) => {
    if (!prize) return '-';
    return new Intl.NumberFormat('ko-KR').format(prize) + '원';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">당첨번호 조회</h1>
        <div className="flex items-center space-x-2">
          <input
            type="number"
            placeholder="회차 검색"
            value={searchDraw}
            onChange={(e) => setSearchDraw(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            검색
          </button>
          {searchDraw && (
            <button
              onClick={resetSearch}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              초기화
            </button>
          )}
        </div>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} onRetry={() => fetchResults(page)} />}

      {!loading && !error && (
        <>
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">회차</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">추첨일</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">당첨번호</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">보너스</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700">1등 당첨금</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.map((result) => (
                  <tr key={result.draw_no} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {result.draw_no}회
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {result.draw_date}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-1">
                        {result.numbers.map((num, idx) => (
                          <LottoBall key={idx} number={num} size="sm" />
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <LottoBall number={result.bonus} size="sm" isBonus />
                    </td>
                    <td className="px-6 py-4 text-sm text-right text-gray-900">
                      {formatPrize(result.prize_1st)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {pagination && pagination.total_pages > 1 && (
            <div className="flex justify-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
              >
                이전
              </button>
              <span className="px-4 py-2">
                {page} / {pagination.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={page === pagination.total_pages}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
              >
                다음
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
