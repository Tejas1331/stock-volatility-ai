type Props = {
    data: any;
  };
  
  export default function JsonViewer({ data }: Props) {
    return (
      <pre className="text-xs bg-gray-900 text-green-200 p-4 rounded-lg overflow-x-auto max-h-96">
        {JSON.stringify(data, null, 2)}
      </pre>
    );
  }
  