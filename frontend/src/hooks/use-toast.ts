import toast from 'react-hot-toast'

const defaultStyle = {
  borderRadius: '8px',
  background: 'hsl(var(--card))',
  color: 'hsl(var(--foreground))',
  border: '1px solid hsl(var(--border))',
}

export function useToast() {
  return {
    success: (message: string) =>
      toast.success(message, {
        style: defaultStyle,
        duration: 3000,
      }),
    error: (message: string) =>
      toast.error(message, {
        style: defaultStyle,
        duration: 4000,
      }),
    info: (message: string) =>
      toast(message, {
        icon: 'ℹ️',
        style: defaultStyle,
      }),
    loading: (message: string) =>
      toast.loading(message, {
        style: defaultStyle,
      }),
    dismiss: (id?: string) => toast.dismiss(id),
  }
}
