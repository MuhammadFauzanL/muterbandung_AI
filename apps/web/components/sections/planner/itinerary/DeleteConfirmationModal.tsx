import { Trash2 } from 'lucide-react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
}

export function DeleteConfirmationModal({ isOpen, onClose, onConfirm, title }: DeleteConfirmationModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-[360px] rounded-[24px] bg-white p-8 text-center shadow-xl border border-[#0E75BC]">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-[#FCD3D1]">
          <Trash2 className="h-6 w-6 text-[#E94B35]" />
        </div>
        <h3 className="mb-4 text-[18px] font-bold text-[#112F43] leading-snug">
          Yakin ingin menghapus<br />destinasi ini?
        </h3>
        <p className="mb-8 text-[12px] leading-5 text-[#557083]">
          {title} akan dihapus dari itinerary perjalananmu. Perubahan ini dapat memengaruhi estimasi biaya dan rute perjalanan. Kamu tetap dapat menambahkannya kembali kapan saja.
        </p>
        <div className="flex justify-center gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-full border border-slate-300 bg-white py-2.5 text-xs font-bold text-[#112F43] transition-colors hover:bg-slate-50 shadow-sm"
          >
            Batal
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 rounded-full bg-[#E94B35] py-2.5 text-xs font-bold text-white transition-colors hover:bg-[#c93f2b] shadow-sm"
          >
            Hapus Destinasi
          </button>
        </div>
      </div>
    </div>
  );
}
