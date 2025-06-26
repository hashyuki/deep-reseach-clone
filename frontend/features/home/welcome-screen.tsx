import { InputForm } from './input-form'

type WelcomeScreenProps = {
  handleSubmit: (submittedInputValue: string, effort: string, model: string) => void
  onCancel: () => void
  isLoading: boolean
}

export function WelcomeScreen({
  handleSubmit,
  onCancel,
  isLoading,
}: WelcomeScreenProps) {
  return (
  <div className='mx-auto flex h-full w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-4 text-center'>
    <div>
      <h1 className='mb-3 text-5xl font-semibold text-neutral-100 md:text-6xl'>Welcome.</h1>
      <p className='text-xl text-neutral-400 md:text-2xl'>How can I help you today?</p>
    </div>
    <div className='mt-4 w-full'>
      <InputForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={false}
      />
    </div>
    <p className='text-xs text-neutral-500'>Powered by OpenAI and Tavily with LangChain LangGraph.</p>
  </div>
  )
}
