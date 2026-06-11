/**
 * Utility Functions
 *
 * Shared helper functions used across the frontend application.
 */

/**
 * Join class names conditionally.
 * Lightweight alternative to clsx/classnames for simple cases.
 */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Format price for Indonesian Rupiah display.
 */
export function formatRupiah(value: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value);
}
