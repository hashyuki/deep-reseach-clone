import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Activity,
  Brain,
  ChevronDown,
  ChevronUp,
  Info,
  Loader2,
  Pen,
  Search,
  TextSearch,
} from 'lucide-react'
import { useEffect, useState } from 'react'

export type ProcessedEvent = {
  id: string
  title: string
  data: any
}

type ActivityTimelineProps = {
  processedEvents: ProcessedEvent[]
  isLoading: boolean
}

// Event type mapping for better type safety
type EventType = 'generating' | 'thinking' | 'reflection' | 'research' | 'finalizing' | 'default'

// Icon mapping configuration
const EVENT_ICONS: Record<EventType, React.ComponentType<{ className?: string }>> = {
  generating: TextSearch,
  thinking: Loader2,
  reflection: Brain,
  research: Search,
  finalizing: Pen,
  default: Activity,
}

// Helper function to determine event type from title
function getEventType(title: string): EventType {
  const lowerTitle = title.toLowerCase()

  if (lowerTitle.includes('generating')) return 'generating'
  if (lowerTitle.includes('thinking')) return 'thinking'
  if (lowerTitle.includes('reflection')) return 'reflection'
  if (lowerTitle.includes('research')) return 'research'
  if (lowerTitle.includes('finalizing')) return 'finalizing'

  return 'default'
}

// Helper function to format event data
function formatEventData(data: any): string {
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return data.join(', ')
  return JSON.stringify(data)
}

// Loading event component
type LoadingEventProps = {
  isFirstEvent?: boolean
}

function LoadingEvent({ isFirstEvent = false }: LoadingEventProps) {
  return (
  <div className='relative pb-4 pl-8'>
    <div className='absolute left-3 top-3.5 h-full w-0.5 bg-neutral-800' />
    <div
      className={`absolute left-0.5 top-2 flex items-center justify-center rounded-full ring-4 ring-neutral-900 ${
        isFirstEvent ? 'h-5 w-5 bg-neutral-800' : 'h-5 w-5 bg-neutral-600 ring-neutral-700'
      }`}
    >
      <Loader2 className='h-3 w-3 animate-spin text-neutral-400' />
    </div>
    <div>
      <p className='text-sm font-medium text-neutral-300'>Searching...</p>
    </div>
  </div>
  )
}

// Empty state component
function EmptyState() {
  return (
  <div className='flex h-full flex-col items-center justify-center pt-10 text-neutral-500'>
    <Info className='mb-3 h-6 w-6' />
    <p className='text-sm'>No activity to display.</p>
    <p className='mt-1 text-xs text-neutral-600'>Timeline will update during processing.</p>
  </div>
  )
}

// Individual event component
type TimelineEventProps = {
  event: ProcessedEvent
  index: number
  totalEvents: number
  isLoading: boolean
}

function TimelineEvent({ event, index, totalEvents, isLoading }: TimelineEventProps) {
  const eventType = getEventType(event.title)
  const IconComponent = EVENT_ICONS[eventType]
  const showConnector = index < totalEvents - 1 || (isLoading && index === totalEvents - 1)
  const isAnimated = eventType === 'thinking' || (index === 0 && isLoading && totalEvents === 0)

  return (
    <div className='relative pb-4 pl-8'>
      {showConnector && <div className='absolute left-3 top-3.5 h-full w-0.5 bg-neutral-600' />}
      <div className='absolute left-0.5 top-2 flex h-6 w-6 items-center justify-center rounded-full bg-neutral-600 ring-4 ring-neutral-700'>
        <IconComponent className={`h-4 w-4 text-neutral-400 ${isAnimated ? 'animate-spin' : ''}`} />
      </div>
      <div>
        <p className='mb-0.5 text-sm font-medium text-neutral-200'>{event.title}</p>
        <p className='text-xs leading-relaxed text-neutral-300'>{formatEventData(event.data)}</p>
      </div>
    </div>
  )
}

export function ActivityTimeline({ processedEvents, isLoading }: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] = useState<boolean>(false)

  // Auto-collapse timeline when processing completes
  useEffect(() => {
    if (!isLoading && processedEvents.length > 0) {
      setIsTimelineCollapsed(true)
    }
  }, [isLoading, processedEvents])

  const toggleTimeline = () => setIsTimelineCollapsed(!isTimelineCollapsed)

  return (
    <Card className='max-h-96 rounded-lg border-none bg-neutral-700'>
      <CardHeader>
        <CardDescription className='flex items-center justify-between'>
          <div
            className='flex w-full cursor-pointer items-center justify-start gap-2 text-sm text-neutral-100'
            onClick={toggleTimeline}
          >
            Research
            {isTimelineCollapsed ? (
              <ChevronDown className='mr-2 h-4 w-4' />
            ) : (
              <ChevronUp className='mr-2 h-4 w-4' />
            )}
          </div>
        </CardDescription>
      </CardHeader>

      {!isTimelineCollapsed && (
        <ScrollArea className='max-h-96 overflow-y-auto'>
          <CardContent>
            {/* Show loading state when no events exist */}
            {isLoading && processedEvents.length === 0 && <LoadingEvent isFirstEvent={true} />}

            {/* Show events if they exist */}
            {processedEvents.length > 0 && (
              <div className='space-y-0'>
                {processedEvents.map((event, index) => (
                  <TimelineEvent
                    key={event.id || `event-${index}`}
                    event={event}
                    index={index}
                    totalEvents={processedEvents.length}
                    isLoading={isLoading}
                  />
                ))}

                {/* Show loading indicator at the end if still processing */}
                {isLoading && <LoadingEvent />}
              </div>
            )}

            {/* Show empty state when not loading and no events */}
            {!isLoading && processedEvents.length === 0 && <EmptyState />}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  )
}
