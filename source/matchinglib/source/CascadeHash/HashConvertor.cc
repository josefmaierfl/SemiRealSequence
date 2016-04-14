#include "..\..\include\CascadeHash\HashConvertor.h"

#include <cmath>
#include <cstdlib>
#include <cstring>

HashConvertor::HashConvertor()
{
    // generate the projection matrix for the primary hashing function (for Hamming distance ranking)
    for (int index_1 = 0; index_1 < kDimHashData; index_1++)
    {
        for (int index_2 = 0; index_2 < kDimSiftData; index_2++)
        {
            projMatPriTr[index_1][index_2] = static_cast<int>(GetNormRand() * 1000);
        }
    }

    // generate the projection matrix for the secondary hashing function (for bucket construction)
    for (int groupIndex = 0; groupIndex < kCntBucketGroup; groupIndex++)
    {
        for (int index_1 = 0; index_1 < kCntBucketBit; index_1++)
        {
            for (int index_2 = 0; index_2 < kDimSiftData; index_2++)
            {
                projMatSecTr[groupIndex][index_1][index_2] = static_cast<int>(GetNormRand() * 1000);
            }
        }
    }

    // generate the selected bit list (for bucket construction)
    // bits are selected from the Hash code generated by the primary hashing function
    for (int groupIndex = 0; groupIndex < kCntBucketGroup; groupIndex++)
    {
        uint8_t bitUsedList[kDimHashData];
        memset(bitUsedList, 0, kDimHashData); // initialize the bit usage flag array

        for (int bitIndex = 0; bitIndex < kCntBucketBit; bitIndex++)
        {
            int bitSel = -1;
            do
            {
                bitSel = rand() % kDimHashData;
            }   while (bitUsedList[bitSel] == 1); // ensure the selected bit has not been used for this bucket

            bitUsedList[bitSel] = 1;
            bucketBitList[groupIndex][bitIndex] = bitSel;
        }
    }
}

void HashConvertor::SiftDataToHashData(ImageData& imageData)
{
    // allocate space for <hashDataPtrList>, <compHashDataPtrList> and <bucketIDList>
    imageData.hashDataPtrList = (HashDataPtr*)malloc(sizeof(HashDataPtr) * imageData.cntPoint); 
    imageData.compHashDataPtrList = (CompHashDataPtr*)malloc(sizeof(CompHashDataPtr) * imageData.cntPoint);
    for (int groupIndex = 0; groupIndex < kCntBucketGroup; groupIndex++)
    {
        imageData.bucketIDList[groupIndex] = (uint16_t*)malloc(sizeof(uint16_t) * imageData.cntPoint);
    }

    for (int dataIndex = 0; dataIndex < imageData.cntPoint; dataIndex++)
    {
        // allocate space for each SIFT point
        imageData.hashDataPtrList[dataIndex] = (uint8_t*)malloc(sizeof(uint8_t) * kDimHashData);
        imageData.compHashDataPtrList[dataIndex] = (uint64_t*)malloc(sizeof(uint64_t) * kDimCompHashData);

        // obtain pointers for SIFT feature vector, Hash code and CompHash code
        SiftDataPtr siftDataPtr = imageData.siftDataPtrList[dataIndex];
        HashDataPtr hashDataPtr = imageData.hashDataPtrList[dataIndex];
        CompHashDataPtr compHashDataPtr = imageData.compHashDataPtrList[dataIndex];
        
        // calculate the Hash code: H = PX
        // H: Hash code vector, Nx1 vector, N = kDimHashData
        // P: projection matrix, NxM matrix, M = kDimSiftData
        // X: SIFT feature vector, Mx1 vector
        for (int dimHashIndex = 0; dimHashIndex < kDimHashData; dimHashIndex++)
        {
            int sum = 0;
            int* projVec = projMatPriTr[dimHashIndex];
            for (int dimSiftIndex = 0; dimSiftIndex < kDimSiftData; dimSiftIndex++)
            {
                if (siftDataPtr[dimSiftIndex] != 0)
                {
                    sum += siftDataPtr[dimSiftIndex] * projVec[dimSiftIndex]; // matrix multiplication
                }
            }
            hashDataPtr[dimHashIndex] = (sum > 0) ? 1 : 0; // use 0 as the threshold
        }
        
        // calculate the CompHash code
        // compress <kBitInCompHash> Hash code bits within a single <uint64_t> variable
        for (int dimCompHashIndex = 0; dimCompHashIndex < kDimCompHashData; dimCompHashIndex++)
        {
            uint64_t compHashBitVal = 0;
            int dimHashIndexLBound = dimCompHashIndex * kBitInCompHash;
            int dimHashIndexUBound = (dimCompHashIndex + 1) * kBitInCompHash;
            for (int dimHashIndex = dimHashIndexLBound; dimHashIndex < dimHashIndexUBound; dimHashIndex++)
            {
                compHashBitVal = (compHashBitVal << 1) + hashDataPtr[dimHashIndex]; // set the corresponding bit to 1/0
            }
            compHashDataPtr[dimCompHashIndex] = compHashBitVal;
        }

        // determine the bucket index for each bucket group
        for (int groupIndex = 0; groupIndex < kCntBucketGroup; groupIndex++)
        {
            uint16_t bucketID = 0;
            for (int bitIndex = 0; bitIndex < kCntBucketBit; bitIndex++)
            {
            #ifdef Bucket_SecHash // use secondary hashing function to determine the bucket index
                int sum = 0;
                int* projVec = projMatSecTr[groupIndex][bitIndex];
                for (int dimSiftIndex = 0; dimSiftIndex < kDimSiftData; dimSiftIndex++)
                {
                    if (siftDataPtr[dimSiftIndex] != 0)
                    {
                        sum += siftDataPtr[dimSiftIndex] * projVec[dimSiftIndex]; // matrix multiplication
                    }
                }
                bucketID = (bucketID << 1) + (sum > 0 ? 1 : 0);
            #endif // Bucket_SecHash
            #ifdef Bucket_PriHashSel // use selected bits in primary hashing result to determine the bucket index
                bucketID = (bucketID << 1) + hashDataPtr[bucketBitList[groupIndex][bitIndex]];
            #endif // Bucket_PriHashSel
            }
            imageData.bucketIDList[groupIndex][dataIndex] = bucketID;
        }
    }
}

double HashConvertor::GetNormRand(void)
{
    // based on Box-Muller transform; for more details, please refer to the following WIKIPEDIA website:
    // http://en.wikipedia.org/wiki/Box_Muller_transform
    double u1 = (rand() % 1000 + 1) / 1000.0;
    double u2 = (rand() % 1000 + 1) / 1000.0;

    double randVal = sqrt(-2 * log(u1)) * cos(2 * acos(-1.0) * u2);

    return randVal;
}
