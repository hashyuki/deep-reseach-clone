'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ActivityTimeline, type ProcessedEvent } from '@/features/home/activity-timeline'
import { InputForm } from '@/features/home/input-form'
import { cn } from '@/lib/utils'
import type { Message } from '@langchain/langgraph-sdk'
import { Copy, CopyCheck } from 'lucide-react'
import { type ReactNode, useCallback, useState } from 'react'
import ReactMarkdown from 'react-markdown'

// Type definitions
type MdComponentProps = {
  className?: string
  children?: ReactNode
  [key: string]: any
}

type MessageBubbleProps = {
  message: Message
}

type AiMessageBubbleProps = MessageBubbleProps & {
  historicalActivity?: ProcessedEvent[]
  liveActivity?: ProcessedEvent[]
  isLastMessage: boolean
  isOverallLoading: boolean
  onCopy: (text: string, messageId: string) => void
  copiedMessageId: string | null
}

type ChatMessagesViewProps = {
  messages: Message[]
  isLoading: boolean
  scrollAreaRef: React.RefObject<HTMLDivElement | null>
  onSubmit: (inputValue: string, effort: string, model: string) => void
  onCancel: () => void
  liveActivityEvents: ProcessedEvent[]
  historicalActivities: Record<string, ProcessedEvent[]>
}

// Markdown components (from former ReportView.tsx)
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn('mb-2 mt-4 text-2xl font-bold', className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn('mb-2 mt-3 text-xl font-bold', className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn('mb-1 mt-3 text-lg font-bold', className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn('mb-3 leading-7', className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => {
    // Extract domain from URL for display with error handling
    let displayText: string
    try {
      if (href) {
        const url = new URL(href)
        displayText = url.hostname.replace('www.', '')
      } else {
        displayText = String(children)
      }
    } catch (error) {
      // Fallback to children if URL parsing fails
      displayText = String(children)
    }

    return (
      <Badge className='mx-0.5 border border-blue-500/30 bg-blue-600/20 text-xs transition-colors hover:bg-blue-600/30'>
        <a
          className={cn(
            'flex items-center gap-1 text-xs text-blue-400 no-underline hover:text-blue-300',
            className,
          )}
          href={href}
          target='_blank'
          rel='noopener noreferrer'
          title={href ? `Open ${href}` : undefined}
          {...props}
        >
          <span className='max-w-[150px] truncate'>{displayText}</span>
        </a>
      </Badge>
    )
  },
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn('mb-3 list-disc pl-6', className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn('mb-3 list-decimal pl-6', className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn('mb-1', className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn('my-3 border-l-4 border-neutral-600 pl-4 text-sm italic', className)}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn('rounded bg-neutral-900 px-1 py-0.5 font-mono text-xs', className)}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        'my-3 overflow-x-auto rounded-lg bg-neutral-900 p-3 font-mono text-xs',
        className,
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn('my-4 border-neutral-600', className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className='my-3 overflow-x-auto'>
      <table className={cn('w-full border-collapse', className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn('border border-neutral-600 px-3 py-2 text-left font-bold', className)}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td className={cn('border border-neutral-600 px-3 py-2', className)} {...props}>
      {children}
    </td>
  ),
}

// Extract message content helper
function getMessageContent(message: Message): string {
  if (typeof message.content === 'string') {
    return message.content
  }
  return JSON.stringify(message.content)
}

// Human Message Bubble Component
function HumanMessageBubble({ message }: MessageBubbleProps) {
  return (
    <div
      className={`min-h-7 max-w-[100%] break-words rounded-3xl rounded-br-lg bg-neutral-700 px-4 pt-3 text-white sm:max-w-[90%]`}
    >
      <ReactMarkdown components={mdComponents}>{getMessageContent(message)}</ReactMarkdown>
    </div>
  )
}

// AI Message Bubble Component
function AiMessageBubble({
  message,
  historicalActivity,
  liveActivity,
  isLastMessage,
  isOverallLoading,
  onCopy,
  copiedMessageId,
}: AiMessageBubbleProps) {
  const isLiveActivity = isLastMessage && isOverallLoading
  const activityEvents = isLiveActivity ? liveActivity : historicalActivity
  const hasActivity = activityEvents && activityEvents.length > 0
  const showMessage = !isLiveActivity && message.content

  return (
    <div className={`relative flex flex-col break-words`}>
      {/* Activity Timeline */}
      {(isLiveActivity || hasActivity) && (
        <div className='mb-3 border-b border-neutral-700 pb-3 text-xs'>
          <ActivityTimeline processedEvents={activityEvents || []} isLoading={isLiveActivity} />
        </div>
      )}
      {/* Message Content */}
      {showMessage && (
        <>
          <ReactMarkdown components={mdComponents}>{getMessageContent(message)}</ReactMarkdown>
          <Button
            variant='default'
            className='cursor-pointer self-end border-neutral-600 bg-neutral-700 text-neutral-300'
            onClick={() => onCopy(getMessageContent(message), message.id!)}
          >
            {copiedMessageId === message.id ? (
              <>
                Copied <CopyCheck className='ml-1 h-4 w-4' />
              </>
            ) : (
              <>
                Copy <Copy className='ml-1 h-4 w-4' />
              </>
            )}
          </Button>
        </>
      )}
    </div>
  )
}

// Loading State Component
type LoadingStateProps = {
  liveActivityEvents: ProcessedEvent[]
}

function LoadingState({ liveActivityEvents }: LoadingStateProps) {
  return (
    <div className='mt-3 flex items-start gap-3'>
      <div className='group relative w-full max-w-[85%] break-words md:max-w-[80%]'>
        <div className='border-b border-neutral-700 pb-3 text-xs'>
          <ActivityTimeline processedEvents={liveActivityEvents} isLoading={true} />
        </div>
      </div>
    </div>
  )
}

// Message Component
type MessageItemProps = {
  message: Message
  isLast: boolean
  isLoading: boolean
  liveActivityEvents: ProcessedEvent[]
  historicalActivities: Record<string, ProcessedEvent[]>
  onCopy: (text: string, messageId: string) => void
  copiedMessageId: string | null
}

function MessageItem({
  message,
  isLast,
  isLoading,
  liveActivityEvents,
  historicalActivities,
  onCopy,
  copiedMessageId,
}: MessageItemProps) {
  return (
    <div className='space-y-3'>
      <div className={cn('flex items-start gap-3', message.type === 'human' && 'justify-end')}>
        {message.type === 'human' ? (
          <HumanMessageBubble message={message} />
        ) : (
          <div className='w-full max-w-[85%] md:max-w-[80%]'>
            <AiMessageBubble
              message={message}
              historicalActivity={historicalActivities[message.id!]}
              liveActivity={liveActivityEvents}
              isLastMessage={isLast}
              isOverallLoading={isLoading}
              onCopy={onCopy}
              copiedMessageId={copiedMessageId}
            />
          </div>
        )}
      </div>
    </div>
  )
}

// Main Component
export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)

  const handleCopy = useCallback(async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageId(messageId)
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }, [])

  const shouldShowLoading =
    isLoading && (messages.length === 0 || messages[messages.length - 1]?.type === 'human')

  return (
    <div className='flex h-full flex-col'>
      <ScrollArea className='flex-1 overflow-y-auto' ref={scrollAreaRef}>
        <div className='mx-auto max-w-4xl space-y-2 p-4 pt-16 md:p-6'>
          {messages.map((message, index) => {
            // Generate a more unique key combining ID, index, and timestamp
            const uniqueKey = message.id ? `${message.id}-${index}` : `msg-${index}-${Date.now()}`

            return (
              <MessageItem
                key={uniqueKey}
                message={message}
                isLast={index === messages.length - 1}
                isLoading={isLoading}
                liveActivityEvents={liveActivityEvents}
                historicalActivities={historicalActivities}
                onCopy={handleCopy}
                copiedMessageId={copiedMessageId}
              />
            )
          })}

          {shouldShowLoading && <LoadingState liveActivityEvents={liveActivityEvents} />}
        </div>
      </ScrollArea>
      <InputForm
        onSubmit={onSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={messages.length > 0}
      />
    </div>
  )
}
