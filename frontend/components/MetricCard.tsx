type Props = {
    label: string;
    value: string;
  };
  
  export default function MetricCard({ label, value }: Props) {
    return (
      <div className="flex flex-col bg-gray-50 border rounded-lg p-4">
        <span className="text-sm text-gray-500">{label}</span>
        <span className="text-lg font-semibold text-gray-900">
          {value}
        </span>
      </div>
    );
  }
  