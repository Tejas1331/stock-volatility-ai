type Props = {
    risk: "low" | "medium" | "high";
  };
  
  const colorMap = {
    low: "bg-green-100 text-green-800 border-green-300",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
    high: "bg-red-100 text-red-800 border-red-300",
  };
  
  export default function RiskBadge({ risk }: Props) {
    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-semibold border ${colorMap[risk]}`}
      >
        {risk.toUpperCase()}
      </span>
    );
  }
  