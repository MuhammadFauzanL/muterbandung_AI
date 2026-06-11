import { EXPLORE_CATEGORY_FILTERS } from '@/constants';

export function CategoryChips() {
  return (
    <div className="flex flex-wrap gap-2">
      {EXPLORE_CATEGORY_FILTERS.map((filter, index) => (
        <button
          key={filter}
          type="button"
          className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
            index === 0
              ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
              : 'border-[#D5E6F2] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC]'
          }`}
        >
          {filter}
        </button>
      ))}
    </div>
  );
}
