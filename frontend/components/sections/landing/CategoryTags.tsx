export function CategoryTags() {
  const tags = ['Alam', 'Keluarga', 'Kuliner', 'Healing', 'Edukasi', 'Populer', 'Favorite'];

  return (
    <section className="bg-white py-6">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="flex flex-wrap gap-3">
          {tags.map((tag) => (
            <button
              key={tag}
              type="button"
              className="rounded-full border border-[#EAF6FC] bg-[#F3F8FC] px-5 py-2 text-[13px] font-medium text-[#14528E] transition-colors hover:border-[#0E75BC] hover:bg-[#EEF7FD]"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
