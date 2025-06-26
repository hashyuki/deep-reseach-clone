import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Brain, Cpu, Send, SquarePen, StopCircle, Zap } from 'lucide-react'
import { useState } from 'react'

// Updated InputFormProps
type InputFormProps = {
  onSubmit: (inputValue: string, effort: string, model: string) => void
  onCancel: () => void
  isLoading: boolean
  hasHistory: boolean
}

export function InputForm({ onSubmit, onCancel, isLoading, hasHistory }: InputFormProps) {
  const [internalInputValue, setInternalInputValue] = useState('')
  const [effort, setEffort] = useState('medium')
  const [model, setModel] = useState('gpt-4o-mini')

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!internalInputValue.trim()) return
    onSubmit(internalInputValue, effort, model)
    setInternalInputValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleInternalSubmit()
    }
  }

  const isSubmitDisabled = !internalInputValue.trim() || isLoading

  return (
    <form onSubmit={handleInternalSubmit} className={`flex flex-col gap-2 p-3 pb-4`}>
      <div
        className={`flex flex-row items-center justify-between rounded-3xl rounded-bl-sm text-white ${
          hasHistory ? 'rounded-br-sm' : ''
        } min-h-7 break-words bg-neutral-700 px-4 pt-3`}
      >
        <Textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Who won the Euro 2024 and scored the most goals?'
          className={`max-h-[200px] min-h-[56px] w-full resize-none border-0 text-neutral-100 placeholder-neutral-500 shadow-none outline-none focus:outline-none focus:ring-0 focus-visible:ring-0 md:text-base`}
          rows={1}
        />
        <div className='-mt-3'>
          {isLoading ? (
            <Button
              type='button'
              variant='ghost'
              size='icon'
              className='cursor-pointer rounded-full p-2 text-red-500 transition-all duration-200 hover:bg-red-500/10 hover:text-red-400'
              onClick={onCancel}
            >
              <StopCircle className='h-5 w-5' />
            </Button>
          ) : (
            <Button
              type='submit'
              variant='ghost'
              className={`${
                isSubmitDisabled
                  ? 'text-neutral-500'
                  : 'text-blue-500 hover:bg-blue-500/10 hover:text-blue-400'
              } cursor-pointer rounded-full p-2 text-base transition-all duration-200`}
              disabled={isSubmitDisabled}
            >
              Search
              <Send className='h-5 w-5' />
            </Button>
          )}
        </div>
      </div>
      <div className='flex items-center justify-between'>
        <div className='flex flex-row gap-2'>
          <div className='flex max-w-[100%] flex-row gap-2 rounded-xl rounded-t-sm border-neutral-600 bg-neutral-700 pl-2 text-neutral-300 focus:ring-neutral-500 sm:max-w-[90%]'>
            <div className='flex flex-row items-center text-sm'>
              <Brain className='mr-2 h-4 w-4' />
              Effort
            </div>
            <Select value={effort} onValueChange={setEffort}>
              <SelectTrigger className='w-[120px] cursor-pointer border-none bg-transparent'>
                <SelectValue placeholder='Effort' />
              </SelectTrigger>
              <SelectContent className='cursor-pointer border-neutral-600 bg-neutral-700 text-neutral-300'>
                <SelectItem
                  value='low'
                  className='cursor-pointer hover:bg-neutral-600 focus:bg-neutral-600'
                >
                  Low
                </SelectItem>
                <SelectItem
                  value='medium'
                  className='cursor-pointer hover:bg-neutral-600 focus:bg-neutral-600'
                >
                  Medium
                </SelectItem>
                <SelectItem
                  value='high'
                  className='cursor-pointer hover:bg-neutral-600 focus:bg-neutral-600'
                >
                  High
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className='flex max-w-[100%] flex-row gap-2 rounded-xl rounded-t-sm border-neutral-600 bg-neutral-700 pl-2 text-neutral-300 focus:ring-neutral-500 sm:max-w-[90%]'>
            <div className='ml-2 flex flex-row items-center text-sm'>
              <Cpu className='mr-2 h-4 w-4' />
              Model
            </div>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger className='w-[150px] cursor-pointer border-none bg-transparent'>
                <SelectValue placeholder='Model' />
              </SelectTrigger>
              <SelectContent className='cursor-pointer border-neutral-600 bg-neutral-700 text-neutral-300'>
                <SelectItem
                  value='gpt-4o'
                  className='cursor-pointer hover:bg-neutral-600 focus:bg-neutral-600'
                >
                  <div className='flex items-center'>
                    <Zap className='mr-2 h-4 w-4 text-green-400' /> GPT-4o
                  </div>
                </SelectItem>
                <SelectItem
                  value='gpt-4o-mini'
                  className='cursor-pointer hover:bg-neutral-600 focus:bg-neutral-600'
                >
                  <div className='flex items-center'>
                    <Zap className='mr-2 h-4 w-4 text-blue-400' /> GPT-4o Mini
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        {hasHistory && (
          <Button
            className='cursor-pointer rounded-xl rounded-t-sm border-neutral-600 bg-neutral-700 pl-2 text-neutral-300'
            variant='default'
            onClick={() => window.location.reload()}
          >
            <SquarePen size={16} />
            New Search
          </Button>
        )}
      </div>
    </form>
  )
}
