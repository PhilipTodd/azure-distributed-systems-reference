FROM mcr.microsoft.com/dotnet/aspnet@sha256:de0ee358cdd672f7017a003bed21e9ac9ed48a27c922a59b18175b6e82fa7fee
WORKDIR /app
COPY publish/ ./
ENV ASPNETCORE_URLS=http://+:8080
ENV DOTNET_GCHeapHardLimit=0x8000000
USER app
EXPOSE 8080
ENTRYPOINT ["dotnet", "Stage1.HostingProbe.dll"]
