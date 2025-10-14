import boto3
from botocore.exceptions import ClientError
import io
from PIL import Image
import os
from typing import Optional
import hashlib
import aiofiles
from pathlib import Path


class StorageService:
    """سرویس مدیریت ذخیره‌سازی ابری و محلی"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        self.use_s3 = os.getenv("USE_S3", "false").lower() == "true"
        
        if self.use_s3:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                print(f"✅ S3 Storage initialized: {self.bucket_name}")
            except Exception as e:
                print(f"⚠️  S3 initialization failed: {e}. Falling back to local storage.")
                self.use_s3 = False
        else:
            print("📁 Using local file storage")
    
    async def upload_image(
        self,
        image_data: bytes,
        filename: str,
        folder: str = "generated",
        optimize: bool = True
    ) -> str:
        """
        آپلود تصویر به S3 یا ذخیره محلی
        
        Args:
            image_data: داده تصویر به صورت bytes
            filename: نام فایل
            folder: پوشه ذخیره‌سازی
            optimize: بهینه‌سازی تصویر قبل از آپلود
            
        Returns:
            URL تصویر آپلود شده
        """
        
        # بهینه‌سازی تصویر
        if optimize:
            image_data = await self._optimize_image(image_data)
        
        # محاسبه hash برای نام یکتا
        file_hash = hashlib.md5(image_data).hexdigest()[:12]
        file_ext = Path(filename).suffix or '.jpg'
        unique_filename = f"{file_hash}_{filename.replace(file_ext, '')}{file_ext}"
        
        if self.use_s3 and self.s3_client:
            return await self._upload_to_s3(image_data, folder, unique_filename)
        else:
            return await self._upload_local(image_data, folder, unique_filename)
    
    async def _optimize_image(
        self,
        image_data: bytes,
        max_width: int = 1280,
        quality: int = 85
    ) -> bytes:
        """
        بهینه‌سازی تصویر (resize, compress)
        
        Args:
            image_data: داده تصویر
            max_width: حداکثر عرض تصویر
            quality: کیفیت فشرده‌سازی (1-100)
            
        Returns:
            داده تصویر بهینه شده
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Resize اگر بزرگتر از max_width باشد
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB اگر RGBA باشد
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save با compression
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_data = output.getvalue()
            
            print(f"🎨 Image optimized: {len(image_data)} → {len(optimized_data)} bytes ({len(optimized_data)/len(image_data)*100:.1f}%)")
            
            return optimized_data
        except Exception as e:
            print(f"⚠️  Image optimization failed: {e}. Using original.")
            return image_data
    
    async def _upload_to_s3(self, image_data: bytes, folder: str, filename: str) -> str:
        """آپلود به Amazon S3"""
        key = f"{folder}/{filename}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType='image/jpeg',
                CacheControl='public, max-age=31536000',
                ACL='public-read'
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            print(f"☁️  Uploaded to S3: {url}")
            return url
            
        except ClientError as e:
            print(f"❌ S3 upload error: {e}")
            # Fallback to local
            return await self._upload_local(image_data, folder, filename)
    
    async def _upload_local(self, image_data: bytes, folder: str, filename: str) -> str:
        """ذخیره محلی"""
        upload_dir = Path("uploads") / folder
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data)
        
        relative_path = f"/uploads/{folder}/{filename}"
        print(f"💾 Saved locally: {relative_path}")
        return relative_path
    
    async def download_from_url(self, url: str) -> bytes:
        """دانلود تصویر از URL"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"Failed to download image: {response.status}")
    
    async def add_watermark(
        self,
        image_data: bytes,
        watermark_text: str = "Routix.ai",
        position: str = "bottom-right"
    ) -> bytes:
        """
        افزودن واترمارک به تصویر
        
        Args:
            image_data: داده تصویر
            watermark_text: متن واترمارک
            position: موقعیت (top-left, top-right, bottom-left, bottom-right, center)
            
        Returns:
            داده تصویر با واترمارک
        """
        try:
            from PIL import ImageDraw, ImageFont
            
            image = Image.open(io.BytesIO(image_data))
            
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Calculate text size
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            margin = 20
            if position == "bottom-right":
                x = image.width - text_width - margin
                y = image.height - text_height - margin
            elif position == "bottom-left":
                x = margin
                y = image.height - text_height - margin
            elif position == "top-right":
                x = image.width - text_width - margin
                y = margin
            elif position == "top-left":
                x = margin
                y = margin
            else:  # center
                x = (image.width - text_width) // 2
                y = (image.height - text_height) // 2
            
            # Draw semi-transparent background
            padding = 10
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 128)
            )
            
            # Draw text
            draw.text((x, y), watermark_text, fill=(255, 255, 255, 200), font=font)
            
            # Save
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=90)
            
            print(f"🏷️  Watermark added: {watermark_text}")
            return output.getvalue()
            
        except Exception as e:
            print(f"⚠️  Watermark failed: {e}. Returning original.")
            return image_data


# Singleton instance
storage_service = StorageService()
